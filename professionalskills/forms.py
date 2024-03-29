#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ValidationError

from general_form import FileForm, clean_file_default
from general_model import get_ext, print_list

from templates import widgets
from timeline.utils import get_timeslot
from .models import FileType, StaffResponse, StudentGroup, FileExtension, StaffResponseFileAspectResult, StaffResponseFileAspect, StudentFile


class FileTypeModelForm(forms.ModelForm):

    def save(self, commit=True):
        if self.errors:
            raise ValueError(
                "The %s could not be %s because the data didn't validate." % (
                    self.instance._meta.object_name,
                    'created' if self.instance._state.adding else 'changed',
                )
            )
        self.instance.TimeSlot = get_timeslot()
        self.instance.save()
        self._save_m2m()
        return self.instance

    class Meta:
        model = FileType

        fields = [
            'Name',
            'Deadline',
            'Description',
            'AllowedExtensions',
            'CheckedBySupervisor'
        ]

        widgets = {
            'Name': widgets.MetroTextInput,
            'Deadline': widgets.MetroDateInput,
            'Description': widgets.MetroTextInput,
            'AllowedExtensions': widgets.MetroSelectMultiple,
            'CheckedBySupervisor': widgets.MetroCheckBox,
        }
        labels = {
            'AllowedExtensions': 'Allowed file extensions',
            'CheckedBySupervisor': 'Supervisor check',
        }
        help_texts = {
            'CheckedBySupervisor': 'Check this box if the supervisor of the project has to review and grade this professional skill.',
            'AllowedExtensions': 'If more extensions are needed, edit them using the professionalskills->extensions menu',
        }

        def clean(self):
            cleaned_data = super().clean()
            # Title should be unique within one timeslot, a new filetype is always created in the current timeslot.
            title = cleaned_data.get('Name')
            p = FileType.objects.filter(TimeSlot=get_timeslot(), Name__iexact=title)
            if p.exists():
                for conflict_or_self in p:
                    if conflict_or_self.id != self.instance.id:
                        raise ValidationError('A professional skill with this name already exists in this timeslot')
            return cleaned_data


class StaffResponseForm(forms.ModelForm):
    """
    A response from a staff member to a professionalskill file of a student.
    """

    class Meta:
        model = StaffResponse

        fields = [
            'Explanation',
            'Status',
        ]
        widgets = {
            'Explanation': widgets.MetroMultiTextInput,
            'Status': widgets.MetroSelect,
        }


class StudentGroupForm(forms.ModelForm):
    """
    A group of students for a PRV
    """

    class Meta:
        model = StudentGroup
        fields = [
            'PRV',
            'Number',
            'Start',
            'Max',
        ]
        widgets = {
            'PRV': widgets.MetroSelect,
            'Number': widgets.MetroNumberInputInteger,
            'Start': widgets.MetroDateTimeInput,
            'Max': widgets.MetroNumberInputInteger,
        }
        labels = {
            'PRV': 'Professional skill',
            'Number': 'Group number',
            'Start': 'Start date',
            'Max': 'Max group size',
        }
        help_texts = {
            'Number': 'A unique index number of this group',
            'Max': 'The maximum number of students in this group',
        }

    def clean(self):
        cleaned_data = super().clean()
        new_number = cleaned_data.get('Number')
        g = StudentGroup.objects.filter(Number=new_number, PRV=cleaned_data.get('PRV'))
        if new_number in g.exclude(id=self.instance.id).values_list('Number', flat=True):
            raise ValidationError('Group with that number already exists for this professional skill')
        return cleaned_data


class StudentGroupChoice(forms.Form):
    """

    """
    Group = forms.ModelChoiceField(queryset=StudentGroup.objects.none(), widget=widgets.MetroSelect)

    def __init__(self, *args, **kwargs):
        self.PRV = kwargs.pop('PRV')
        super().__init__(*args, **kwargs)
        self.fields['Group'].queryset = self.PRV.groups


class FileExtensionForm(forms.ModelForm):
    """
    Used in modelform factory to choose file extensions available for student uploading files.
    """

    class Meta:
        model = FileExtension
        fields = [
            'Name',
        ]
        widgets = {
            'Name': widgets.MetroTextInput,
        }


class StaffResponseFileAspectForm(forms.ModelForm):
    class Meta:
        model = StaffResponseFileAspect
        fields = ['Name', 'Description']
        widgets = {
            'Name': widgets.MetroTextInput,
            'Description': widgets.MetroMultiTextInput,
        }


class StaffResponseFileAspectResultForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        disabled = kwargs.pop('disabled', False)
        super().__init__(*args, **kwargs)
        self.fields['Grade'].disabled = disabled

    class Meta:
        model = StaffResponseFileAspectResult
        fields = ['Grade']
        widgets = {
            'Grade': widgets.MetroSelectRadioTable
        }


class StudentFileForm(FileForm):
    """
    Upload or edit a studentfile
    """

    def __init__(self, *args, **kwargs):
        self.filetype = kwargs.pop('filetype')
        super().__init__(*args, **kwargs)
        self.fields['File'].widget.attrs['accept'] = str(','.join(['.' + f for f in self.filetype.AllowedExtensions.values_list('Name', flat=True)]))

    class Meta(FileForm.Meta):
        model = StudentFile
        fields = ['File', 'Caption']
        widgets = {
            'File': widgets.MetroFileInput,
            'Caption': widgets.MetroTextInput,
        }

    def clean_File(self):
        file = clean_file_default(self)
        if get_ext(file.name) not in self.filetype.get_allowed_extensions():
            raise ValidationError('This file extension is not allowed. Allowed extensions: '
                                  + print_list(self.filetype.get_allowed_extensions()))
        return file
