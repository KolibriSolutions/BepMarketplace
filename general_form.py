#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
"""
General functions, mostly used in forms (forms.py)
"""

from django import forms
from django.conf import settings
from django.forms import ValidationError

from professionalskills.models import StudentFile
from templates import widgets


def clean_file_default(self, required=True):
    """
    A check for an uploaded file. Checks filesize.

    :param self:
    :param required: Whether it is required to have a file.
    :return:
    """
    file = self.cleaned_data.get("File")
    if file:
        s = file.size
        if s > settings.MAX_UPLOAD_SIZE:
            raise ValidationError(
                "The file is too large, it has to be at most " + str(
                    round(settings.MAX_UPLOAD_SIZE / 1024 / 1024)) + "MB and is " + str(
                    round(s / 1024 / 1024)) + "MB.")
    elif required:
        raise ValidationError("No file supplied!")
    return file


class FileForm(forms.ModelForm):
    """
    A form to upload a file. It has a filefield and a caption field. More fields can be added.
    """

    class Meta:
        model = StudentFile  # when inherited, this model is usually overwritten. Studentfile is only used as default.
        fields = ['Caption', 'File']
        widgets = {
            'Caption': widgets.MetroTextInput,
            'File': widgets.MetroFileInput
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean_File(self):
        """

        :return:
        """
        return clean_file_default(self)

    def save(self, commit=True):
        """

        :param commit:
        :return:
        """
        instance = super().save(commit=False)
        if 'File' in self.changed_data:
            instance.OriginalName = instance.File.name
        if commit:
            instance.save()
        return instance


class ConfirmForm(forms.Form):
    """Form to confirm a action. Used for extra validation. Not linked to a model."""
    confirm = forms.BooleanField(widget=widgets.MetroCheckBox, label='Confirm:')


class CsvUpload(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # show only csv in file selection dialog
        self.fields['csvfile'].widget.attrs['accept'] = '.csv'

    csvfile = forms.FileField(widget=widgets.MetroFileInput)
    delimiter = forms.ChoiceField(widget=widgets.MetroSelect, choices=(
        (',', ','),
        (';', ';')
    ))

    def clean_csvfile(self):
        file = self.cleaned_data.get("csvfile")
        if not file:
            raise ValidationError("No file supplied!")

        if file.content_type != 'text/csv' and file.content_type != 'application/vnd.ms-excel':
            raise ValidationError("Not a csv file!")
