import re
from datetime import datetime

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.images import get_image_dimensions
from django.forms import ValidationError

from general_form import clean_file_default, FileForm
from general_mail import mailPrivateStudent, mail_proposal_single
from general_model import get_ext
from general_view import get_grouptype, get_timephase_number, get_timeslot
from templates import widgets
from timeline.models import TimeSlot
from tracking.models import ProposalStatusChange
from .models import Proposal, ProposalImage, ProposalAttachment

mailPattern = re.compile(settings.EMAILREGEXCHECK)

#minimal image dimensions.
minw = 30
minh = 30


def clean_image_default(self):
    """
    Check whether an uploaded image is valid and has right dimensions

    :param self:
    :return:
    """
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
    """
    Check whether an attachment is valid

    :param self:
    :return:
    """

    file = clean_file_default(self)
    if get_ext(file.name) not in settings.ALLOWED_PROPOSAL_ATTACHEMENTS:
        raise ValidationError("This filetype is not allowed. Allowed types: "+str(settings.ALLOWED_PROPOSAL_ATTACHEMENTS))
    return file


def get_or_create_user_email(self, email, username, student):
    """
    Get or create a user account

    :param self:
    :param email: emailaddress of the user to find
    :param username: username of the user to find
    :param student: whether the user is a student
    :return: a useraccount, either an existing or a newly created account
    """
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
    """
    Create a new user based on its email address. This user is updated with a real username as soon as the person logs in for the first time.

    :param self:
    :param email: emailaddres
    :param username: username to create, usually a part of the emailaddress
    :param student: whether the users is a student. If false, user is added to the assistants group
    :return: THe created user account
    """
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
    return new_account


class ProposalForm(forms.ModelForm):
    """
    Form to create a proposal
    """
    addAssistantsEmail = forms.CharField(label='Extra assistants (email, one per line)',
                                         widget=widgets.MetroMultiTextInput,
                                         required=False)
    addPrivatesEmail = forms.CharField(label='Private students (email, one per line)',
                                       widget=widgets.MetroMultiTextInput,
                                       required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields['ResponsibleStaff'].queryset = get_grouptype("1").user_set.all()
        self.fields['Assistants'].queryset = get_grouptype("2").user_set.all() | \
                                             get_grouptype("2u").user_set.all() | \
                                             get_grouptype("1").user_set.all()
        self.fields['addAssistantsEmail'].widget.attrs['placeholder'] = "Add assistant via email address"
        self.fields['addPrivatesEmail'].widget.attrs['placeholder'] = "Add private student via email address"

        if get_timephase_number() == 1:
            self.fields['TimeSlot'].queryset = TimeSlot.objects.filter(End__gt=datetime.now())
            self.fields['TimeSlot'].initial = get_timeslot()
        else:
            self.fields['TimeSlot'].queryset = TimeSlot.objects.filter(Begin__gt=datetime.now())

    class Meta:
        model = Proposal
        fields = ['Title',
                  'ResponsibleStaff',
                  'Assistants',
                  'addAssistantsEmail',
                  'Track',
                  'Group',
                  'ECTS',
                  'NumstudentsMin',
                  'NumstudentsMax',
                  'GeneralDescription',
                  'StudentsTaskDescription',
                  'TimeSlot',
                  'addPrivatesEmail'
                  ]

        labels = {
            'ResponsibleStaff': "Responsible staff",
            'ECTS': "Preferred ECTS",
            'NumstudentsMin': "Minimum number of students",
            'NumstudentsMax': "Maximum number of students",
            'GeneralDescription': "General description",
            'StudentsTaskDescription': "Students task description",
            'TimeSlot': 'Timeslot (year)',
            'Private': 'Change private students',
        }
        widgets = {
            'Title': widgets.MetroTextInput,
            'ResponsibleStaff': widgets.MetroSelect,
            'Assistants': widgets.MetroSelectMultiple,
            'Track': widgets.MetroSelect,
            'Group': widgets.MetroSelect,
            'ECTS': widgets.MetroSelect,
            'NumstudentsMin': widgets.MetroNumberInputInteger,
            'NumstudentsMax': widgets.MetroNumberInputInteger,
            'GeneralDescription': widgets.MetroMultiTextInput,
            'StudentsTaskDescription': widgets.MetroMultiTextInput,
            'TimeSlot': widgets.MetroSelect,
            'Private': widgets.MetroSelectMultiple
        }

    def clean(self):
        cleaned_data = super().clean()
        # validate min and max students
        mins = cleaned_data.get("NumstudentsMin")
        maxs = cleaned_data.get("NumstudentsMax")
        if mins and maxs:
            if mins > maxs:
                raise ValidationError("Minimum number of students cannot be higher than maximum.")
        else:
            raise ValidationError("Min or max number of students cannot be empty")
        return cleaned_data

    def clean_addAssistantsEmail(self):
        data = self.cleaned_data['addAssistantsEmail']
        if data == '' or data is None:
            return data
        for email in data.split('\n'):
            email = email.lower().strip('\r').strip()
            if not mailPattern.match(email):
                raise forms.ValidationError(
                    "Invalid email address ({}): Every line should contain one valid email address".format(email))
            domain = email.split('@')[1]
            if domain not in settings.ALLOWED_PROPOSAL_ASSISTANT_DOMAINS:
                raise forms.ValidationError("This email domain is not allowed. Allowed domains: {}".
                                        format(settings.ALLOWED_PROPOSAL_ASSISTANT_DOMAINS))
        return data

    def clean_addPrivatesEmail(self):
        data = self.cleaned_data['addPrivatesEmail']
        if data == '' or data is None:
            return data
        for email in data.split('\n'):
            email = email.lower().strip('\r').strip()
            if not mailPattern.match(email):
                raise forms.ValidationError(
                    "Invalid email address ({}): Every line should contain one valid email address".format(email))
            domain = email.split('@')[1]
            domain_list = ["student.tue.nl"]
            if domain not in domain_list:
                raise forms.ValidationError("Please only enter *@student.tue.nl email addresses")
        return data

    def clean_Assistants(self):
        # Prevent the supervisor of this project to be added as assistant.
        assistants = list(self.cleaned_data['Assistants'])
        try:
            responsible = self.cleaned_data['ResponsibleStaff']
        except:
            raise ValidationError("The responsible staff is missing.")
        if assistants == '' or assistants is None:
            return None
        for ass in assistants:
            if ass == responsible:
                raise ValidationError("The responsible staff cannot be assistant of the same proposal.")
        return assistants

    def save(self, commit=True):
        if commit:
            super().save(commit=True)
            # add assistants to proposal via email.
            # These assistants will get an (extra) email, because they don't know marketplace yet.
            if self.cleaned_data['addAssistantsEmail'] != '' and self.cleaned_data['addAssistantsEmail'] is not None:
                for email in self.cleaned_data['addAssistantsEmail'].split('\n'):
                    email = email.strip('\r').strip().lower()
                    username = email.split('@')[0].replace('.', '')
                    new_account = get_or_create_user_email(self, email, username, False)
                    if new_account and new_account not in self.instance.Assistants.all():
                        self.instance.Assistants.add(new_account)
                        mail_proposal_single(self.request, self.instance, new_account, "You were added as assistant to:")

            # add private students to proposal via email
            if self.cleaned_data['addPrivatesEmail'] != '' and self.cleaned_data['addPrivatesEmail'] is not None:
                for email in self.cleaned_data['addPrivatesEmail'].split('\n'):
                    email = email.strip('\r').strip().lower()
                    username = "student-" + email.split('@')[0].replace('.', '')
                    new_account = get_or_create_user_email(self, email, username, True)
                    if new_account:
                        self.instance.Private.add(new_account)
                        # Mailing the private student is done in the view.

            # if no assistants, set to status 2
            if self.instance.Assistants.count() == 0 and self.instance.Status == 1:
                self.instance.Status = 2

        self.instance.save()
        return self.instance


class ProposalFormEdit(ProposalForm):
    """
    Add the field to remove private students for the editform.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['Private'].queryset = User.objects.filter(groups=None)
        # memorize responsible to be able to mail them if needed
        self.oldResponsibleStaff = self.instance.ResponsibleStaff

    def clean(self):
        cleaned_data = super().clean()
        # Title should be unique within one timeslot.
        title = cleaned_data.get('Title')
        try:
            p = Proposal.objects.filter(TimeSlot=self.cleaned_data['TimeSlot'])
        except:
            p = Proposal.objects.filter(TimeSlot__isnull=True)
        p=p.filter(Title__iexact=title)
        if p.exists():
            for conflict_or_self in p:
                if conflict_or_self.id != self.instance.id:
                    raise ValidationError("A proposal with this title already exists in this timeslot")
        return cleaned_data

    def save(self, commit=True):
        if commit:
            if 'Assistants' in self.changed_data:
                # assistant removed via dropdown
                for ass in self.instance.Assistants.all():
                    if ass not in self.cleaned_data['Assistants']:
                        mail_proposal_single(self.request, self.instance, ass, "You were removed as assistant from:")
                # new assistant added via dropdown
                for ass in self.cleaned_data['Assistants']:
                    if ass not in self.instance.Assistants.all():
                        mail_proposal_single(self.request, self.instance, ass, "You were added as assistant to:")

            if 'Private' in self.changed_data:
                # private student removed via dropdown
                for std in self.instance.Private.all():
                    if std not in self.cleaned_data['Private']:
                        # self.instance.Private.remove(std)
                        mailPrivateStudent(self.request, self.instance, std, "You were removed from your private proposal. If this is unexpected, please contact your supervisor or responsible staff member." )
                # new private student added via dropdown
                # for std in self.cleaned_data['Private']:
                #     if std not in self.instance.Private.all():
                        # self.instance.Private.add(std)
                        # no email, because student gets update email in views.py on edit

            if 'ResponsibleStaff' in self.changed_data:
                if self.instance.ResponsibleStaff != self.oldResponsibleStaff:
                    mail_proposal_single(self.request, self.instance, self.oldResponsibleStaff,
                                         "You were removed as responsible staff from:")
                    mail_proposal_single(self.request, self.instance, self.instance.ResponsibleStaff,
                                         "You were added as responsible staff to:")
            # only save here, because old data is needed to determine changed privates.
            super().save(commit=True)
            self.instance.save()
        return self.instance

    class Meta(ProposalForm.Meta):
        fields= ProposalForm.Meta.fields + ['Private']
        pass


class ProposalFormCreate(ProposalForm):
    """
    Also set the status based on who made the proposal.
    """
    def clean(self):
        cleaned_data = super().clean()
        # Title should be unique within one timeslot.
        title = cleaned_data.get('Title')
        try:
            p = Proposal.objects.filter(TimeSlot=self.cleaned_data['TimeSlot'])
        except:
            p = Proposal.objects.filter(TimeSlot__isnull=True)
        if p.filter(Title__iexact=title).exists():
            raise ValidationError("A proposal with this title already exists in this timeslot")
        return cleaned_data

    def save(self, commit=True):
        if commit:
            super().save(commit=True)
            # if type2 created this proposal
            if get_grouptype("2")in self.request.user.groups.all() or \
                get_grouptype("2u") in self.request.user.groups.all():
                self.instance.Assistants.add(self.request.user)  # in case assistant forgets to add itself
            # if there are no assistants attached go to status 2
            if not self.instance.Assistants.exists():
                self.instance.Status = 2
            self.instance.save()
        return self.instance


class ProposalImageForm(FileForm):
    class Meta(FileForm.Meta):
        model = ProposalImage

    def clean_File(self):
        return clean_image_default(self)


class ProposalAttachmentForm(FileForm):
    class Meta(FileForm.Meta):
        model = ProposalAttachment

    def clean_File(self):
        return clean_attachment_default(self)


class ProposalDowngradeMessageForm(forms.ModelForm):
    class Meta:
        model = ProposalStatusChange
        fields = ['Message']
        widgets = {
            'Message': widgets.MetroMultiTextInput,
        }
        labels = {"Message": "Message, leave blank for no message"}
