#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
from django import forms
from django.conf import settings

from general_model import get_ext
from .models import OsirisDataFile


class OsirisDataFileForm(forms.ModelForm):
    class Meta:
        model = OsirisDataFile

        fields = [
            'File',
            # 'TimeSlot'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['File'].widget.attrs['accept'] = '.xlsx'

    def clean_File(self):
        """
        A check for an uploaded file. Checks filesize.

        :param self:
        :return:
        """
        file = self.cleaned_data.get("File")
        if file:
            s = file.size
            if s > settings.MAX_UPLOAD_SIZE:
                raise forms.ValidationError(
                    "The file is too large, it has to be at most " + str(
                        round(settings.MAX_UPLOAD_SIZE / 1024 / 1024)) + "MB and is " + str(
                        round(s / 1024 / 1024)) + "MB.")

            if get_ext(self.cleaned_data.get('File').name) != 'xlsx':
                raise forms.ValidationError(f'File extension is not allowed, allowed extensions .xlsx')
        return file
