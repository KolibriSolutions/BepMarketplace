from datetime import datetime

from django import forms

from templates import widgets
from .models import TimeSlot, TimePhase


class TimeSlotForm(forms.ModelForm):
    """
    Form to edit a timeslot
    """

    class Meta:
        model = TimeSlot
        fields = ['Name', 'Begin', 'End']
        widgets = {
            'Name': widgets.MetroTextInput,
            'Begin': widgets.MetroDateInput,
            'End': widgets.MetroDateInput,
        }

    def clean(self):
        if self.cleaned_data['End'] < datetime.now().date():
            raise forms.ValidationError('End date cannot be in the past.')


class TimePhaseForm(forms.ModelForm):
    """
    Form to edit/create a timephase
    """

    class Meta:
        model = TimePhase
        fields = ['Description', 'Begin', 'End', 'CountdownEnd', 'Timeslot']
        labels = {
            'CountdownEnd': 'Countdown end',
        }
        widgets = {
            'Description': widgets.MetroSelect,
            'Begin': widgets.MetroDateInput,
            'End': widgets.MetroDateInput,
            'CountdownEnd': widgets.MetroDateInput,
            'Timeslot': widgets.MetroSelect,
        }

    def clean(self):
        if self.cleaned_data['End'] < datetime.now().date():
            raise forms.ValidationError('End date cannot be in the past.')
