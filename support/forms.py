from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, Group
from django.forms import ValidationError

from general_view import get_grouptype
from general_form import clean_file_default, FileForm
from general_model import GroupOptions
from general_model import get_ext, print_list
from index.models import UserMeta
from support.models import CapacityGroupAdministration
from templates import widgets
from .models import PublicFile


def clean_publicfile_default(self):
    file = clean_file_default(self)
    if get_ext(file.name) not in settings.ALLOWED_PUBLIC_FILES:
        raise ValidationError('This file type is not allowed. Allowed types: '
                              + print_list(settings.ALLOWED_PUBLIC_FILES))
    return file


class ChooseMailingList(forms.Form):
    """List to choose what people to mail"""

    def __init__(self, *args, **kwargs):
        options = kwargs.pop('options')
        super().__init__(*args, **kwargs)
        for option in options:
            self.fields['people_{}'.format(option[0])] = forms.BooleanField(widget=widgets.MetroCheckBox,
                                                                            label=option[1],
                                                                            required=False)

    subject = forms.CharField(widget=widgets.MetroTextInput,
                              label='Subject: (leave empty for default)',
                              required=False)
    message = forms.CharField(widget=widgets.MetroMultiTextInput,
                              label='Message (check this twice):')


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


class CapacityGroupAdministrationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['AdministrationMembers'].queryset = User.objects.all()

    def save(self):
        cleaned_data = self.clean()

        if "AdministrationMembers" not in cleaned_data:
            cleaned_data["AdministrationMembers"] = []

        obj = CapacityGroupAdministration.objects.get(Group=cleaned_data['Group'])

        for member in obj.Members.all():
            # remove type4staff for removed members
            if member not in cleaned_data['AdministrationMembers']:
                member.groups.remove(Group.objects.get(name='type4staff'))
                obj.Members.remove(member)
                member.save()

        for member in cleaned_data['AdministrationMembers']:
            # add type4staff to new members
            if member not in obj.Members.all():
                member.groups.add(Group.objects.get(name='type4staff'))
                obj.Members.add(member)
                member.save()

        obj.save()

    Group = forms.ChoiceField(choices=GroupOptions, widget=widgets.MetroSelect)
    AdministrationMembers = forms.ModelMultipleChoiceField(queryset=User.objects.none(),
                                                           widget=widgets.MetroSelectMultiple, required=False,
                                                           label='Administration members')
