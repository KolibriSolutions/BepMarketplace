#  Bep Marketplace ELE
#  Copyright (c) 2016-2021 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from datetime import datetime

from django import forms

from templates import widgets
from .models import TimeSlot, TimePhase
from general_model import clean_text


class TimeSlotForm(forms.ModelForm):
    """
    Form to edit a time slot
    """

    class Meta:
        model = TimeSlot
        fields = ['Name', 'Begin', 'End']
        widgets = {
            'Name': widgets.MetroTextInput,
            'Begin': widgets.MetroDateInput,
            'End': widgets.MetroDateInput,
        }

    def clean_End(self):
        if self.cleaned_data.get('End') < datetime.now().date():
            raise forms.ValidationError('End date cannot be in the past.')
        return self.cleaned_data.get('End')


class TimePhaseForm(forms.ModelForm):
    """
    Form to edit/create a time phase
    """

    class Meta:
        model = TimePhase
        fields = ['Description', 'Begin', 'End', 'CountdownEnd', 'TimeSlot']
        labels = {
            'CountdownEnd': 'Countdown end',
        }
        widgets = {
            'Description': widgets.MetroSelect,
            'Begin': widgets.MetroDateInput,
            'End': widgets.MetroDateInput,
            'CountdownEnd': widgets.MetroDateInput,
            'TimeSlot': widgets.MetroSelect,
        }

    def clean_End(self):
        if self.cleaned_data.get('End') < datetime.now().date():
            raise forms.ValidationError('End date cannot be in the past.')
        return self.cleaned_data.get('End')


class TimePhaseCopyForm(forms.Form):
    """
    Form to copy time phases
    """
    ts_from = forms.ModelChoiceField(queryset=TimeSlot.objects.filter(timephases__isnull=False).distinct(),
                                     widget=widgets.MetroSelect,
                                     help_text='Time slot with time phases to copy time phases from.')
    ts_to = forms.ModelChoiceField(queryset=TimeSlot.objects.filter(timephases__isnull=True, End__gt=datetime.now()).distinct(),
                                   widget=widgets.MetroSelect,
                                   help_text='Time slot to copy time phases to. Only time slots without time phases can be chosen.')


class UserTimeSlotForm(forms.Form):
    timeslot = forms.ModelChoiceField(queryset=TimeSlot.objects.filter(timephases__isnull=False).distinct(),
                                      widget=widgets.MetroSelect,
                                      help_text='Time slot with time phases to copy time phases from.')
    students = forms.CharField(widget=widgets.MetroMultiTextInput,
                               help_text='List of emailaddress of students to change. Student should already have an account. Use a whitespace or newline as delimiter.')

    def clean_students(self):
        return clean_text(self.cleaned_data.get('students'))
