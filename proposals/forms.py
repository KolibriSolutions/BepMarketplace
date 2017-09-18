import re

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.images import get_image_dimensions
from django.forms import ValidationError
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from general_form import clean_file_default, FileForm
from general_mail import send_mail, mailPrivateStudent, mailStaff
from general_model import get_ext
from general_view import get_grouptype, get_timeslot
from templates import widgets
from tracking.models import ProposalStatusChange
from .models import Proposal, ProposalImage, ProposalAttachment

mailPattern = re.compile(settings.EMAILREGEXCHECK)

#minimal image dimensions.
minw = 30
minh = 30

def clean_image_default(self):
    picture = clean_file_default(self)
    if get_ext(picture.name) not in settings.ALLOWED_PROPOSAL_IMAGES:
        raise ValidationError("This filetype is not allowed. Allowed types: "+str(settings.ALLOWED_PROPOSAL_IMAGES))

    w, h = get_image_dimensions(picture)
    if w < minw or h < minh:
        raise ValidationError(
            "The image is too small, it has to be at least " + str(minw) + "px by " + str(
                minh) + "px and is only " + str(
                w) + "px by " + str(
                h) + "px.")

    return picture


def clean_attachment_default(self):
    file = clean_file_default(self)
    if get_ext(file.name) not in settings.ALLOWED_PROPOSAL_ATTACHEMENTS:
        raise ValidationError("This filetype is not allowed. Allowed types: "+str(settings.ALLOWED_PROPOSAL_ATTACHEMENTS))
    return file

def get_or_create_user_email(self, email, username, student):
    try:
        # try both email and username
        try:
            account = User.objects.get(email=email)
        except ObjectDoesNotExist:
            account = User.objects.get(username=username)
        if account == self.instance.ResponsibleStaff:
            return False
        return account
    except ObjectDoesNotExist:
        new_account = create_user_from_email(self, email, username, student)
        return new_account


def create_user_from_email(self, email, username, student=False):
    parts = email.split('@')[0].split('.')
    if parts[-1].isdigit():
        parts.pop()
    lastname = parts.pop()
    firstname = '.'.join(parts) + '.'
    new_account = User.objects.create_user(username, email)
    new_account.first_name = firstname
    new_account.last_name = lastname
    if not student:
        new_account.groups.add(get_grouptype("2u"))
    new_account.save()
    current_site = get_current_site(self.request)
    domain = current_site.domain
    context = {
        'domain': domain,
        'uid': urlsafe_base64_encode(force_bytes(new_account.pk)),
        'user': new_account,
        'token': default_token_generator.make_token(new_account),
    }
    if not student:
        send_mail("email/password_set_email_subject.txt", "email/password_newuser_set_email.html", context,
              "no-reply@ieeesb.nl", new_account.email, html_email_template_name="email/password_newuser_set_email.html")

    return new_account

class ProposalForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields['ResponsibleStaff'].queryset = get_grouptype("1").user_set.all()

    class Meta:
        model = Proposal
        fields = {}
        labels = {
            'ResponsibleStaff': "Responsible staff",
            'ECTS': "Preferred ECTS",
            'NumstudentsMin': "Minimum number of students",
            'NumstudentsMax': "Maximum number of students",
            'GeneralDescription': "General description",
            'StudentsTaskDescription': "Students task description",
        }
        widgets = {
            'Title': widgets.MetroTextInput,
            'GeneralDescription': widgets.MetroMultiTextInput,
            'StudentsTaskDescription': widgets.MetroMultiTextInput,
            'Group': widgets.MetroSelect,
            'ResponsibleStaff': widgets.MetroSelect,
            'ECTS': widgets.MetroSelect,
            'Track': widgets.MetroSelect,
            'Assistants': widgets.MetroSelectMultiple,
            'Private': widgets.MetroSelectMultiple
        }

    def clean(self):
        cleaned_data = super().clean()
        min = cleaned_data.get("NumstudentsMin")
        max = cleaned_data.get("NumstudentsMax")
        if min and max:
            if min > max:
                raise ValidationError("Minimum number of students cannot be higher than maximum.")
            return cleaned_data
        raise ValidationError("Min or max number of students cannot be empty")

    def save(self, commit=True):
        self.instance.save()
        return self.instance


class ProposalFormEdit(ProposalForm):
    addAssistantEmail = forms.CharField(label='Add an assistant (email)', widget=widgets.MetroTextInput,
                                        required=False)
    addPrivateEmail = forms.CharField(label='Add an private student (email)', widget=widgets.MetroTextInput,
                                        required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['addAssistantEmail'].widget.attrs['placeholder'] = "Add another assistant (email address)"
        self.fields['addPrivateEmail'].widget.attrs['placeholder'] = "Add another private student (email address)"
        self.fields['Assistants'].queryset = get_grouptype("2").user_set.all() | \
                                             get_grouptype("2u").user_set.all() | \
                                             get_grouptype("1").user_set.all()
        self.fields['Private'].queryset = User.objects.filter(groups=None)

    def save(self, commit=True):
        if commit:
            if 'Assistants' in self.changed_data:
                #assistant removed via dropdown
                for ass in self.instance.Assistants.all():
                    if ass not in self.cleaned_data['Assistants']:
                        self.instance.Assistants.remove(ass)
                        mailStaff(self.request, self.instance, ass, "You were removed as supervisor from:")
                #new assistant added via dropdown
                for ass in self.cleaned_data['Assistants']:
                    if ass == self.instance.ResponsibleStaff:
                        #prevent responsible staff to add himself as assistant
                        continue
                    if ass not in self.instance.Assistants.all():
                        self.instance.Assistants.add(ass)
                        mailStaff(self.request, self.instance, ass, "You were added as supervisor to:")

            if 'Private' in self.changed_data:
                # private student removed via dropdown
                for std in self.instance.Private.all():
                    if std not in self.cleaned_data['Private']:
                        self.instance.Private.remove(std)
                        mailPrivateStudent(self.request, self.instance, std, "You were removed from your private proposal. If this is unexpected, please contact your supervisor or responsible staff member." )
                # new private student added via dropdown
                for std in self.cleaned_data['Private']:
                    if std not in self.instance.Private.all():
                        self.instance.Private.add(std)
                        #no email, because student gets update email in views.py on edit

            # add extra assistant
            if self.cleaned_data['addAssistantEmail'] != '' and self.cleaned_data['addAssistantEmail'] is not None:
                email = self.cleaned_data['addAssistantEmail']
                email = email.strip().lower()
                username = email.split('@')[0].replace('.', '')
                new_account = get_or_create_user_email(self, email, username, False)
                if new_account:
                    self.instance.Assistants.add(new_account)
                    mailStaff(self.request, self.instance, new_account, "You were added as supervisor to:")

            #add extra private student
            if self.cleaned_data['addPrivateEmail'] != '' and self.cleaned_data['addPrivateEmail'] is not None:
                email = self.cleaned_data['addPrivateEmail']
                email = email.strip().lower()
                username = "student-" + email.split('@')[0].replace('.', '')
                new_account = get_or_create_user_email(self, email, username, True)
                if new_account:
                    self.instance.Private.add(new_account)
                    #no mail here, only in views.py
            if self.instance.Assistants.count() == 0 and self.instance.Status == 1:
                self.instance.Status = 2
            super().save(commit=True)
            self.instance.save()
        return self.instance

    class Meta(ProposalForm.Meta):
        fields = ['Title', 'ResponsibleStaff', 'Assistants', 'addAssistantEmail', 'Track', 'Group', 'ECTS',
                  'Private','addPrivateEmail', 'NumstudentsMin',
                  'NumstudentsMax', 'GeneralDescription',
                  'StudentsTaskDescription']

    def clean_addAssistantEmail(self):
        data = self.cleaned_data['addAssistantEmail']
        if data == '' or data is None:
            return data
        email = data.strip().lower()
        if not mailPattern.match(email):
            raise forms.ValidationError("Invalid email address: This should be one TU/e email address")
        domain = email.split('@')[1]
        domain_list = ["tue.nl"]
        if domain not in domain_list:
            raise forms.ValidationError("Please only enter *@tue.nl email addresses")
        return data

    def clean_addPrivateEmail(self):
        data = self.cleaned_data['addPrivateEmail']
        if data == '' or data is None:
            return data
        email = data.strip().lower()
        if not mailPattern.match(email):
            raise forms.ValidationError("Invalid email address: This should be one TU/e email address")
        domain = email.strip().split('@')[1]
        domain_list = ["student.tue.nl"]
        if domain not in domain_list:
            raise forms.ValidationError("Please only enter *@student.tue.nl email addresses")
        return data


class ProposalFormCreate(ProposalForm):
    assistantsEmail = forms.CharField(label='Assistants email (one per line)', widget=widgets.MetroMultiTextInput, required=False)
    privateEmail = forms.CharField(label='Private student email (one per line)', widget=widgets.MetroMultiTextInput,
                                      required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assistantsEmail'].widget.attrs['placeholder'] = "Add one email address of an assistant per line"
        self.fields['privateEmail'].widget.attrs['placeholder'] = "Add one email address of a private student per line"

    def save(self, commit=True):
        if commit:
            super().save(commit=True)
            # add assistants to proposal
            if self.cleaned_data['assistantsEmail'] != '' and self.cleaned_data['assistantsEmail'] is not None:
                for email in self.cleaned_data['assistantsEmail'].split('\n'):
                    email = email.strip('\r').strip().lower()
                    username = email.split('@')[0].replace('.', '')
                    new_account = get_or_create_user_email(self, email, username, False)
                    if new_account:
                        self.instance.Assistants.add(new_account)
            if self.cleaned_data['privateEmail'] != '' and self.cleaned_data['privateEmail'] is not None:
                for email in self.cleaned_data['privateEmail'].split('\n'):
                    email = email.strip('\r').strip().lower()
                    username = "student-" + email.split('@')[0].replace('.', '')
                    new_account = get_or_create_user_email(self, email, username, True)
                    if new_account:
                        self.instance.Private.add(new_account)

            # if type2 created this proposal
            if get_grouptype("2")in self.request.user.groups.all() or \
                get_grouptype("2u") in self.request.user.groups.all():
                self.instance.Assistants.add(self.request.user)
                self.instance.Status = 2
            else:
                self.instance.Status = 1
            # if there are no assistants attached go to status 2
            if self.instance.Assistants.count() == 0:
                self.instance.Status = 2

            self.instance.save()
        return self.instance

    class Meta(ProposalForm.Meta):
        fields = ['Title', 'ResponsibleStaff', 'assistantsEmail', 'Track', 'Group', 'ECTS', 'privateEmail', 'NumstudentsMin',
                  'NumstudentsMax', 'GeneralDescription',
                  'StudentsTaskDescription']

    def clean_assistantsEmail(self):
        data = self.cleaned_data['assistantsEmail']
        if data == '' or data is None:
            return data
        for email in data.split('\n'):
            email = email.lower()
            if not mailPattern.match(email.strip('\r')):
                raise forms.ValidationError("Invalid email address: Every line should contain one TU/e email address")
            domain = email.strip('\r').split('@')[1]
            domain_list = ["tue.nl",]
            if domain not in domain_list:
                raise forms.ValidationError("Please only enter *@tue.nl email addresses")
        return data

    def clean_privateEmail(self):
        data = self.cleaned_data['privateEmail']
        if data == '' or data is None:
            return data
        for email in data.split('\n'):
            email = email.lower()
            if not mailPattern.match(email.strip('\r')):
                raise forms.ValidationError("Invalid email address: Every line should contain one TU/e email address")
            domain = email.strip('\r').split('@')[1]
            domain_list = ["student.tue.nl"]
            if domain not in domain_list:
                raise forms.ValidationError("Please only enter *@student.tue.nl email addresses")
        return data


class ProposalImageFormAdd(FileForm):
    class Meta(FileForm.Meta):
        model = ProposalImage
    def clean_File(self):
        return clean_image_default(self)


class ProposalImageFormEdit(FileForm):
    class Meta(FileForm.Meta):
        model = ProposalImage
        widgets = {'Caption': widgets.MetroTextInput}
    def clean_File(self):
        return clean_image_default(self)


class ProposalAttachmentFormAdd(FileForm):
    class Meta(FileForm.Meta):
        model = ProposalAttachment
    def clean_File(self):
        return clean_attachment_default(self)


class ProposalAttachmentFormEdit(FileForm):
    class Meta(FileForm.Meta):
        model = ProposalAttachment
        widgets = {'Caption': widgets.MetroTextInput}
    def clean_File(self):
        return clean_attachment_default(self)


class ProposalDowngradeMessageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = ProposalStatusChange
        fields = ['Message']
        widgets = {
            'Message': widgets.MetroMultiTextInput,
        }
        labels = {"Message": "Message, leave blank for no message"}
