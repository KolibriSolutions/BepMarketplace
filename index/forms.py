#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
import re

from django import forms
from django.conf import settings

from templates import widgets
from .models import FeedbackReport, UserMeta, Track
from general_view import get_grouptype

mailPattern = re.compile(settings.EMAILREGEXCHECK)


class FeedbackForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['Url'].widget.attrs['readonly'] = True

    class Meta:
        model = FeedbackReport
        fields = ['Url', 'Feedback']

        widgets = {
            'Feedback': widgets.MetroMultiTextInput,
            'Url': widgets.MetroTextInput,
        }
        labels = {
            'Url': "Page to give feedback on:"
        }


class CloseFeedbackReportForm(forms.Form):
    email = forms.EmailField(label='Sending to:', disabled=True, widget=widgets.MetroTextInput)
    message = forms.CharField(max_length=1024, label='Message:', widget=widgets.MetroMultiTextInput)


class SettingsForm(forms.ModelForm):
    class Meta:
        model = UserMeta
        fields = [
            'SuppressStatusMails'
        ]
        widgets = {
            'SuppressStatusMails': widgets.MetroCheckBox
        }
        labels = {
            'SuppressStatusMails': "Suppress status emails"
        }


class TrackForm(forms.ModelForm):
    """
    Form for tracks, used in modelformsetfactory
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['Name'].disabled = True
        self.fields['ShortName'].disabled = True
        self.fields['Head'].queryset = get_grouptype('1').user_set.all().select_related('usermeta')
        self.fields['Head'].label_from_instance = self.user_label_from_instance

    @staticmethod
    def user_label_from_instance(self):
        return self.usermeta.get_nice_name

    class Meta:
        model = Track
        fields = ['Name', 'ShortName', 'Head']
        widgets = {
            'Name': widgets.MetroTextInput,
            'ShortName': widgets.MetroTextInput,
            'Head': widgets.MetroSelect,
        }
        labels = {
            'ShortName': 'Short name'
        }
