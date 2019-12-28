#  Bep Marketplace ELE
#  Copyright (c) 2016-2019 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, Group
from django.forms import ValidationError

from general_form import clean_file_default, FileForm
from general_model import get_ext, print_list, clean_text
from general_view import get_grouptype
from index.models import UserMeta
from templates import widgets
from timeline.models import TimeSlot
from .models import PublicFile, CapacityGroup


def clean_publicfile_default(self):
    file = clean_file_default(self)
    if get_ext(file.name) not in settings.ALLOWED_PUBLIC_FILES:
        raise ValidationError('This file type is not allowed. Allowed types: '
                              + print_list(settings.ALLOWED_PUBLIC_FILES))
    return file


class ChooseMailingList(forms.Form):
    """
    List to choose what people to mail
    """

    def __init__(self, *args, **kwargs):
        staff_options = kwargs.pop('staff_options')
        student_options = kwargs.pop('student_options')
        super().__init__(*args, **kwargs)
        self.fields['Staff'].choices = staff_options
        self.fields['Students'].choices = student_options

    Subject = forms.CharField(widget=widgets.MetroTextInput,
                              label='Subject:',
                              help_text="Subject for your message. The text '{}' is placed in front of this text".format(settings.NAME_PRETTY),
                              initial='message from support staff')
    Message = forms.CharField(widget=widgets.MetroMultiTextInput,
                              label='Message:',
                              help_text='The body message of the email.')
    Staff = forms.MultipleChoiceField(widget=widgets.MetroSelectMultiple,
                                      label='Staff to mail:',
                                      required=False,
                                      help_text='Only staff with projects in the selected "Only for year" time slot will be mailed',
                                      )
    Students = forms.MultipleChoiceField(widget=widgets.MetroSelectMultiple,
                                         label='Students to mail:',
                                         required=False,
                                         help_text='Only students active in the selected year/timeslot will be mailed.')
    TimeSlot = forms.ModelChoiceField(widget=widgets.MetroSelect,
                                      label='Only for year:',
                                      help_text='Only users active in this year will be mailed.',
                                      queryset=TimeSlot.objects.all())
    SaveTemplate = forms.BooleanField(widget=widgets.MetroCheckBox,
                                      required=False,
                                      label='Save form as template',
                                      help_text='Save this mailing list as template.')

    def clean_Subject(self):
        return clean_text(self.cleaned_data.get('Subject'))

    def clean_Message(self):
        return clean_text(self.cleaned_data.get('Message'))


class PublicFileForm(FileForm):
    """Form to add a public file"""

    class Meta(FileForm.Meta):
        model = PublicFile

    def clean_File(self):
        return clean_publicfile_default(self)


class OverRuleUserMetaForm(forms.ModelForm):
    """Form to overrule the meta of a user. Overruled means that Osiris/LDAP login doesn't override attributes."""

    class Meta:
        model = UserMeta

        fields = [
            'Study',
            'Cohort',
            'EnrolledBEP',
            'EnrolledExt'
        ]

        widgets = {
            'Study': widgets.MetroTextInput,
            'Cohort': widgets.MetroNumberInput,
            'EnrolledBEP': widgets.MetroCheckBox,
            'EnrolledExt': widgets.MetroCheckBox,
        }


class GroupadministratorEdit(forms.Form):
    """
    Form to assign groupadministrators to capacitygroups.
    """
    group = forms.ModelChoiceField(queryset=CapacityGroup.objects.all(), widget=widgets.MetroSelect,
                                   label='Capacity group:')
    readmembers = forms.ModelMultipleChoiceField(queryset=User.objects.filter(groups__isnull=False).distinct(),
                                                 widget=widgets.MetroSelectMultiple,
                                                 required=False, label='Administrators (read):')
    writemembers = forms.ModelMultipleChoiceField(queryset=User.objects.filter(groups__isnull=False).distinct(),
                                                  widget=widgets.MetroSelectMultiple,
                                                  required=False, label='Administrators (read/write):')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['readmembers'].label_from_instance = self.user_label_from_instance
        self.fields['writemembers'].label_from_instance = self.user_label_from_instance

    @staticmethod
    def user_label_from_instance(self):
        return self.usermeta.get_nice_name

    def clean(self):
        """
        Do not allow users to be in both read and write members.
        :return:
        """
        dups = set(self.cleaned_data.get('readmembers')) & set(self.cleaned_data.get('writemembers'))
        if dups:
            raise ValidationError(
                "User(s) {} cannot be both read and write members. Please remove them from one of the fields.".format(
                    print_list(list(dups))))


class UserGroupsForm(forms.ModelForm):
    """Form to assign groups to a user."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['groups'].queryset = Group.objects.exclude(name='type2staffunverified')

    class Meta:
        model = get_user_model()

        fields = ['groups']
        widgets = {'groups': widgets.MetroSelectMultiple}

    def clean_groups(self):
        groups = self.cleaned_data.get('groups')
        if len(groups) > 2:
            raise ValidationError("A user cannot be assigned more than two groups.")
        elif len(groups) == 2:
            # some invalid combinations:
            if get_grouptype('1') in groups and get_grouptype('2') in groups:
                raise ValidationError("A user cannot be both type1staff and type2staff. A proposal can have a type1staff member as assistant instead.")
            if get_grouptype('3') in groups:
                if get_grouptype('4') in groups:
                    raise ValidationError("type3staff has all rights of type4staff also has."
                                          " It is not possible to assign both.")
                if get_grouptype('5') in groups:
                    raise ValidationError("type3staff has all rights of type5staff also has. "
                                          "It is not possible to assign both.")
        return groups


class CapacityGroupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['Head'].queryset = get_grouptype("1").user_set.all()
        self.fields['Head'].label_from_instance = self.user_label_from_instance

    class Meta:
        model = CapacityGroup
        fields = ['ShortName', 'FullName', 'Head']  # not info.
        widgets = {
            'ShortName': widgets.MetroTextInput,
            'FullName': widgets.MetroTextInput,
            'Head': widgets.MetroSelect,
        }

    @staticmethod
    def user_label_from_instance(self):
        return self.usermeta.get_nice_name
