from django import forms
from django.conf import settings
from django.forms import ValidationError

from general_form import clean_file_default, FileForm
from general_model import get_ext, print_list
from index.models import UserMeta
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
