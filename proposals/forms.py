#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
import logging
import re
from datetime import datetime

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import MultipleObjectsReturned
from django.core.files.base import ContentFile
from django.core.files.images import get_image_dimensions
from django.forms import ValidationError

from BepMarketplace.utils import get_user
from general_form import clean_file_default, FileForm
from general_mail import mail_project_private, mail_project_single
from general_model import get_ext, print_list
from general_view import get_grouptype
from index.models import UserMeta
from templates import widgets
from timeline.models import TimeSlot
from timeline.utils import get_timeslot, get_timephase_number
from tracking.models import ProposalStatusChange as ProjectStatusChange
from .models import Proposal as Project
from .models import ProposalImage as ProjectImage
from .models import ProposalAttachment as ProjectAttachment
from .models import ProposalFile as ProjectFile
from proposals.utils import get_writable_admingroups

logger = logging.getLogger('django')

mailPattern = re.compile(settings.EMAILREGEXCHECK)

# minimal image dimensions in px
minw = 30
minh = 30


def clean_image_default(self):
    """
    Check whether an uploaded image is valid and has right dimensions

    :param self:
    :return:
    """
    picture = clean_file_default(self)

    # this check is done both here and in the model, needed to prevent wrong files entering get_image_dimensions()
    if get_ext(picture.name) not in settings.ALLOWED_PROJECT_IMAGES:
        raise ValidationError('This file type is not allowed. Allowed types: '
                              + print_list(settings.ALLOWED_PROJECT_IMAGES))

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
    # this check is done both here and in the model
    if get_ext(file.name) not in settings.ALLOWED_PROJECT_ATTACHMENTS:
        raise ValidationError('This file type is not allowed. Allowed types: '
                              + print_list(settings.ALLOWED_PROJECT_ATTACHMENTS))
    return file


def clean_email_default(email, allowed_domains):
    """
    Clean email address and check if it has allowed domain

    :param email: emailadress in string
    :param allowed_domains: FQDN of allowed domain of mail
    :return: cleaned lowercase email addresss string or ValidationError
    """
    email = email.strip('\r').strip().lower()
    if not mailPattern.match(email):
        raise forms.ValidationError(
            "Invalid email address ({}): Every line should contain one valid email address".format(email))
    # check if the domain is allowed (for instance @tue.nl )
    domain = email.split('@')[1]
    if domain not in allowed_domains:
        raise forms.ValidationError("This email domain is not allowed. Allowed domains: {}".
                                    format(print_list(allowed_domains)))
    return email


def get_or_create_user_email(email, student):
    """
    Get or create a user account

    :param email: emailaddress of the user to find
    :param student: whether the user is a student
    :return: a useraccount, either an existing or a newly created account
    """
    # temporary username till first login of user.
    username = email.split('@')[0].replace('.', '')
    try:
        account = get_user(email, username)  # check account match on email. If not exists check on username.
    except MultipleObjectsReturned:
        logger.error(
            "The user with email {} was added as assistant via emailaddress and has multiple accounts. One account should be removed.".format(
                email))
        return None

    if account:
        return account
    else:
        new_account = create_user_from_email(email, username, student)
        return new_account


def create_user_from_email(email, username, student=False):
    """
    Create a new user based on its email address.
    This user is updated with a real username as soon as the person logs in for the first time.

    :param email: emailaddres
    :param username: username to create, usually a part of the email address
    :param student: whether the users is a student. If false, user is added to the assistants group
    :return: THe created user account
    """
    parts = email.split('@')[0].split('.')
    # strip possible index number at the end.
    if parts[-1].isdigit():
        parts.pop()
    # get all single letters (initials etc)
    initials = ''
    while len(parts[0]) == 1:
        initials += parts.pop(0) + '.'
    # what remains is lastname. Join possible multiple last names.
    last_name = (' '.join(parts)).title()
    initials = initials.title()
    new_account = User.objects.create_user(username, email)
    new_account.first_name = initials
    new_account.last_name = last_name
    if not student:
        new_account.groups.add(get_grouptype('2u'))
    new_account.full_clean()
    new_account.save()
    m = UserMeta(
        User=new_account,
        Initials=initials,
        Fullname="{}, {}".format(last_name, initials),
    )
    m.full_clean()
    m.save()
    return new_account


class ProposalFormLimited(forms.ModelForm):
    """
    Form to change assistants and title on a project
    """
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.support = get_grouptype('3') in self.request.user.groups.all()
        super().__init__(*args, **kwargs)
        self.fields['ResponsibleStaff'].label_from_instance = self.user_label_from_instance
        self.fields['Assistants'].label_from_instance = self.user_label_from_instance
        self.fields['Assistants'].queryset = get_grouptype('2').user_set.all() | \
                                             get_grouptype('2u').user_set.all() | \
                                             get_grouptype('1').user_set.all()
        if not self.support:
            self.fields.pop('ResponsibleStaff')

    @staticmethod
    def user_label_from_instance(self):
        return self.usermeta.get_nice_name

    class Meta:
        model = Project

        fields = [
            'Title',
            'ResponsibleStaff',
            'Assistants'
        ]

        widgets = {
            'Title': widgets.MetroTextInput,
            'ResponsibleStaff' : widgets.MetroSelect,
            'Assistants': widgets.MetroSelectMultiple,
        }

    def clean(self):
        cleaned_data = super().clean()
        # Title should be unique within one timeslot.
        p = Project.objects.filter(TimeSlot=self.instance.TimeSlot).filter(Title__iexact=cleaned_data.get('Title'))
        if p.exists():
            for conflict_or_self in p:
                if conflict_or_self.id != self.instance.id:
                    raise ValidationError('A proposal with this title already exists in this timeslot')
        for account in self.cleaned_data.get('Assistants'):
            if account == self.instance.ResponsibleStaff:
                raise ValidationError("The responsible staff member cannot be assistants of its own project.")
            # for assistants added using email, the queryset is not checked, so check groups now.
            if get_grouptype('2') not in account.groups.all() and \
                    get_grouptype('2u') not in account.groups.all() and \
                    get_grouptype('1') not in account.groups.all():
                raise ValidationError(
                    "The user {} is not allowed as assistant. Please contact the support staff if this user needs to be added.".format(account.usermeta.get_nice_name()))
        return cleaned_data


class ProjectForm(forms.ModelForm):
    """
    Form to create a project.
    """
    # addAssistantsEmail = forms.CharField(label='Extra assistants (email, one per line)',
    #                                      widget=widgets.MetroMultiTextInput,
    #                                      required=False,
    #                                      help_text='Add an assistant using email address. Use this when the assistant cannot be found in the list of assistants')
    addPrivatesEmail = forms.CharField(label='Private students (email, one per line)',
                                       widget=widgets.MetroMultiTextInput,
                                       required=False,
                                       help_text='Add a private student using student email address. Use this when the student cannot be found in the list of students.')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields['ResponsibleStaff'].queryset = get_grouptype('1').user_set.all().select_related('usermeta')
        self.fields['Assistants'].queryset = get_grouptype('2').user_set.all().select_related('usermeta') | \
                                             get_grouptype('2u').user_set.all().select_related('usermeta') | \
                                             get_grouptype('1').user_set.all().select_related('usermeta')
        self.fields['ResponsibleStaff'].label_from_instance = self.user_label_from_instance
        self.fields['Assistants'].label_from_instance = self.user_label_from_instance
        # self.fields['addAssistantsEmail'].widget.attrs['placeholder'] = "Add assistant via email address"
        self.fields['Private'].queryset = User.objects.filter(groups=None).select_related('usermeta')
        self.fields['Private'].label_from_instance = self.user_label_from_instance

        # no user label_from_instance for private students because privacy.
        self.fields['addPrivatesEmail'].widget.attrs['placeholder'] = "Add private student via email address"

        if get_timephase_number() == 1:
            self.fields['TimeSlot'].queryset = TimeSlot.objects.filter(End__gt=datetime.now())
            self.fields['TimeSlot'].initial = get_timeslot()
        else:
            if self.request.user.is_superuser or get_grouptype('3') in self.request.user.groups.all():
                self.fields['TimeSlot'].queryset = TimeSlot.objects.all()
            else:
                # phase 2+, only add for future timeslot
                self.fields['TimeSlot'].queryset = TimeSlot.objects.filter(Begin__gt=datetime.now())

    @staticmethod
    def user_label_from_instance(self):
        return self.usermeta.get_nice_name

    class Meta:
        model = Project
        fields = ['Title',
                  'ResponsibleStaff',
                  'Assistants',
                  # 'addAssistantsEmail',
                  'Track',
                  'Group',
                  'NumStudentsMin',
                  'NumStudentsMax',
                  'GeneralDescription',
                  'StudentsTaskDescription',
                  'ExtensionDescription',
                  'TimeSlot',
                  'addPrivatesEmail',
                  'Private',  # also enabled on Create for resit-students, and for easier form validation.
                  ]

        labels = {
            'NumStudentsMin': 'Minimum number of students',
            'NumStudentsMax': 'Maximum number of students',
            'GeneralDescription': 'General description',
            'StudentsTaskDescription': 'Students task description',
            'ExtensionDescription': 'Description for extension work',
            'TimeSlot': 'Time slot (year)',
            'Private': 'Change private students',
        }
        widgets = {
            'Title': widgets.MetroTextInput,
            'ResponsibleStaff': widgets.MetroSelect,
            'Assistants': widgets.MetroSelectMultiple,
            'Track': widgets.MetroSelect,
            'Group': widgets.MetroSelect,
            'NumStudentsMin': widgets.MetroNumberInputInteger,
            'NumStudentsMax': widgets.MetroNumberInputInteger,
            'GeneralDescription': widgets.MetroMarkdownInput,
            'StudentsTaskDescription': widgets.MetroMarkdownInput,
            'ExtensionDescription': widgets.MetroMarkdownInput,
            'TimeSlot': widgets.MetroSelect,
            'Private': widgets.MetroSelectMultiple
        }
    #
    # def clean_addAssistantsEmail(self):
    #     """
    #     Clean email addresses and check their domain.
    #     convert email to user object, create if not exists.
    #
    #     :return: assistant user accounts, as list
    #     """
    #     data = self.cleaned_data['addAssistantsEmail']
    #     accounts = []
    #     if data:
    #         for email in data.split('\n'):
    #             email = clean_email_default(email, settings.ALLOWED_PROJECT_ASSISTANT_DOMAINS)
    #             account = get_or_create_user_email(email, student=False)
    #             if account:
    #                 accounts.append(account)
    #             else:
    #                 raise ValidationError("User with email {} is invalid. Please contact support staff to resolve this issue.".format(email))
    #     return accounts

    def clean_addPrivatesEmail(self):
        """
        Clean email addresses and check their domain.
        convert email to user object, create if not exists.

        :return: private student user accounts, as list
        """
        data = self.cleaned_data['addPrivatesEmail']
        accounts = []
        if data:
            for email in data.split('\n'):
                email = clean_email_default(email, settings.ALLOWED_PRIVATE_STUDENT_DOMAINS)
                accounts.append(get_or_create_user_email(email, student=True))
        return accounts

    def clean_Group(self):
        group = self.cleaned_data['Group']
        if self.request.user.groups.count() == 1 and get_grouptype('4') in self.request.user.groups.all():
            # user is groupadmin and not assistant/responsible.
            rw_groups = get_writable_admingroups(self.request.user)
            if group not in rw_groups:
                raise ValidationError("You are not allowed to create a project for that group. You are only allowed to "
                                      "create projects for {}".format(print_list(rw_groups)))
        return group

    def clean(self):
        """
        Merge Private and addPrivatesEmail to Private, Merge addAssistantsEmail and Assistants to Assistants
        Verify validity of added users via email.
        Make sure the Private and Assistant dropdown field exist on the form,
        otherwise addAssistantEmail and addPrivateEmail are not saved.

        :return: updated Assistants and Privates
        """
        cleaned_data = super().clean()
        # add and check private students
        privates = []
        if cleaned_data.get('Private'):
            privates += cleaned_data.get('Private')
        if cleaned_data.get('addPrivatesEmail'):
            privates += cleaned_data.get('addPrivatesEmail')
        privates = set(privates)
        for account in privates:
            for p in account.personal_proposal.all():
                if p.TimeSlot == cleaned_data.get('TimeSlot') and p.pk != self.instance.pk:
                    raise ValidationError(
                        "Student {} already has another private proposal!".format(account.usermeta.get_nice_name()))
        cleaned_data['Private'] = privates
        # add and check assistants.
        assistants = []
        if cleaned_data.get('Assistants'):
            assistants += cleaned_data.get('Assistants')
        # if cleaned_data.get('addAssistantsEmail'):
        #     assistants += cleaned_data.get('addAssistantsEmail')
        assistants = set(assistants)
        for account in assistants:
            if account == cleaned_data.get('ResponsibleStaff'):
                raise ValidationError("The responsible staff member cannot be assistants of its own project.")
            # for assistants added using email, the queryset is not checked, so check groups now.
            if get_grouptype('2') not in account.groups.all() and \
                    get_grouptype('2u') not in account.groups.all() and \
                    get_grouptype('1') not in account.groups.all():
                raise ValidationError(
                    "The user {} is not allowed as assistant. Please contact the support staff if this user needs to be added.".format(account.usermeta.get_nice_name()))
        cleaned_data['Assistants'] = assistants
        return cleaned_data

    def save(self, commit=True):
        if commit:
            super().save(commit=True)
            # if no assistants, set to status 2
            if self.instance.Status == 1 and not self.instance.Assistants.exists():
                self.instance.Status = 2
        self.instance.save()
        return self.instance


class ProjectFormEdit(ProjectForm):
    """
    Edit an existing project.
    Mail changed assistants or changed responsible on edit.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # memorize responsible to be able to mail them if needed
        self.oldResponsibleStaff = self.instance.ResponsibleStaff

    class Meta(ProjectForm.Meta):
        pass

    def clean(self):
        cleaned_data = super().clean()
        # Title should be unique within one timeslot.
        p = Project.objects.filter(TimeSlot=self.cleaned_data.get('TimeSlot'))
        p = p.filter(Title__iexact=cleaned_data.get('Title'))
        if p.exists():
            for conflict_or_self in p:
                if conflict_or_self.id != self.instance.id:
                    raise ValidationError('A proposal with this title already exists in this timeslot')
        return cleaned_data

    def save(self, commit=True):
        if commit:
            # add or remove assistants and external and notify them by mail.
            if 'Assistants' in self.changed_data:
                # assistant removed
                for ass in self.instance.Assistants.all():
                    if ass not in self.cleaned_data['Assistants']:
                        mail_project_single(self.instance, ass, "You were removed as assistant from:")
                # new assistant added
                for ass in self.cleaned_data['Assistants']:
                    if ass not in self.instance.Assistants.all():
                        mail_project_single(self.instance, ass, "You were added as assistant to:")
            if 'Private' in self.changed_data:
                # private student
                for std in self.instance.Private.all():
                    if std not in self.cleaned_data['Private']:
                        mail_project_private(self.instance, std, 'You were removed from your private proposal. '
                                                                 'If this is unexpected, please contact your supervisor.')
                # no email on add, because student gets update email in views.py on edit

            if 'ResponsibleStaff' in self.changed_data:
                if self.instance.ResponsibleStaff != self.oldResponsibleStaff:
                    mail_project_single(self.instance, self.oldResponsibleStaff,
                                        "You were removed as responsible staff from:")
                    mail_project_single(self.instance, self.instance.ResponsibleStaff,
                                        "You were added as responsible staff to:")
            # only save here, because old data is needed to determine changed privates.
            super().save(commit=True)
            self.instance.save()
        return self.instance


class ProjectFormCreate(ProjectForm):
    """
    Form to create a project.
    """
    # copy field to store a possible copied proposals original, to be able to copy images/attachments later on.
    copy = forms.ModelChoiceField(queryset=Project.objects.all(), required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        if 'copy' in kwargs.keys():
            pk = kwargs.pop('copy', None)
            super().__init__(*args, **kwargs)
            self.fields['copy'].initial = pk
        else:
            super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        # Title should be unique within one timeslot.
        p = Project.objects.filter(TimeSlot=self.cleaned_data.get('TimeSlot'))
        if p.filter(Title__iexact=cleaned_data.get('Title')).exists():
            raise ValidationError('A proposal with this title already exists in this timeslot')
        return cleaned_data

    def save(self, commit=True):
        if commit:
            super().save(commit=True)
            # if type2 created this project
            if get_grouptype('2') in self.request.user.groups.all() or \
                    get_grouptype('2u') in self.request.user.groups.all():
                self.instance.Assistants.add(self.request.user)  # in case assistant forgets to add itself
            # mailing users on this project is done in the view.
            self.instance.save()
            if self.cleaned_data['copy']:
                # do not copy assistants
                p = self.cleaned_data['copy']
                if p.images.exists():
                    for a in p.images.all():
                        f = ContentFile(a.File.read())
                        b = ProjectImage(
                            Caption=a.Caption,
                            OriginalName=a.OriginalName,
                            Proposal=self.instance,
                        )
                        b.File.save(ProjectFile.make_upload_path(b, a.OriginalName), f, save=False)
                        b.full_clean()  # This will crash hard if an invalid type is supplied, which can't happen
                        b.save()
                if p.attachments.exists():
                    for a in p.attachments.all():
                        f = ContentFile(a.File.read())
                        b = ProjectAttachment(
                            Caption=a.Caption,
                            OriginalName=a.OriginalName,
                            Proposal=self.instance,
                        )
                        b.File.save(ProjectFile.make_upload_path(b, a.OriginalName), f, save=False)
                        b.full_clean()  # This will crash hard if an invalid type is supplied, which can't happen
                        b.save()
        return self.instance


class ProjectImageForm(FileForm):
    class Meta(FileForm.Meta):
        model = ProjectImage

    def clean_File(self):
        return clean_image_default(self)


class ProjectAttachmentForm(FileForm):
    class Meta(FileForm.Meta):
        model = ProjectAttachment

    def clean_File(self):
        return clean_attachment_default(self)


class ProjectDowngradeMessageForm(forms.ModelForm):
    class Meta:
        model = ProjectStatusChange
        fields = ['Message']
        widgets = {
            'Message': widgets.MetroMultiTextInput,
        }
        labels = {"Message": "Message, leave blank for no message"}

# defines for sync with mastermp
ProposalForm = ProjectForm
ProposalFormEdit = ProjectFormEdit
ProposalImageForm = ProjectImageForm
ProposalAttachmentForm = ProjectAttachmentForm
ProposalFormCreate = ProjectFormCreate
ProposalDowngradeMessageForm = ProjectDowngradeMessageForm
