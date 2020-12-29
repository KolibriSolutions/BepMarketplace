#  Bep Marketplace ELE
#  Copyright (c) 2016-2021 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.forms import ValidationError
from django.shortcuts import get_object_or_404

from general_form import clean_file_default, FileForm
from general_model import get_ext, print_list
from timeline.utils import get_timeslot
from professionalskills.models import FileType, FileExtension
from templates import widgets


def clean_studentfile_default(self):
    """
    Clean function for studentfile form. Checks if the extension is in the allowed extensions for this type file.

    :param self:
    :return:
    """
    try:
        ftype = get_object_or_404(FileType, pk=self.data['Type'])
    except:
        raise ValidationError('Please select a file type from the drop-down list.')
    file = clean_file_default(self)
    if get_ext(file.name) not in ftype.get_allowed_extensions():
        raise ValidationError('This file extension is not allowed. Allowed extensions: '
                              + print_list(ftype.get_allowed_extensions()))
    return file


class StudentFileForm(FileForm):
    """
    Upload or edit a studentfile
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['Type'].queryset = FileType.objects.filter(TimeSlot=get_timeslot())
        # allow any extension known in the system, full validation is done afterwards based on the filetype.
        self.fields['File'].widget.attrs['accept'] = str(','.join(['.'+f for f in FileExtension.objects.all().values_list('Name', flat=True)]))

    class Meta(FileForm.Meta):
        fields = ['File', 'Caption', 'Type']
        widgets = {
           'File': widgets.MetroFileInput,
           'Caption': widgets.MetroTextInput,
           'Type': widgets.MetroSelect
        }

    def clean_File(self):
        return clean_studentfile_default(self)
