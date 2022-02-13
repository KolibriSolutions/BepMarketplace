#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from datetime import time

from django import forms

from general_view import get_grouptype
from templates import widgets
from timeline.utils import get_timeslot
from .models import PresentationSet, PresentationOptions, Room


class PresentationOptionsForm(forms.ModelForm):
    """
    Global options (guidelines) for all presentations. All presentations link back to this.
    """

    def save(self, commit=True):
        if commit:
            self.instance.TimeSlot = get_timeslot()
            self.instance.Public = False
            super().save(commit=True)
            self.instance.save()
        return self.instance

    class Meta:
        model = PresentationOptions
        fields = ['PresentationDuration', 'AssessmentDuration', 'PresentationsBeforeAssessment']
        labels = {
            'PresentationDuration': "Duration of the presentation (minutes)",
            'AssessmentDuration': "Duration of the assessment (minutes)",
            'PresentationsBeforeAssessment': "Number of presentations before assessment",
        }
        widgets = {
            'PresentationDuration': widgets.MetroNumberInput,
            'AssessmentDuration': widgets.MetroNumberInput,
            'PresentationsBeforeAssessment': widgets.MetroNumberInput,
        }


class PresentationSetForm(forms.ModelForm):
    """
    A set of presentations. A set is a number of presentations in the same room for one track.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['Assessors'].label_from_instance = self.user_label_from_instance
        self.fields['Assessors'].queryset = get_grouptype('2').user_set.all().select_related('usermeta') | \
                                            get_grouptype('2u').user_set.all().select_related('usermeta') | \
                                            get_grouptype('1').user_set.all().select_related('usermeta')
        self.fields['PresentationAssessors'].label_from_instance = self.user_label_from_instance
        self.fields['PresentationAssessors'].queryset = get_grouptype('7').user_set.all().select_related('usermeta')

    @staticmethod
    def user_label_from_instance(self):
        return self.usermeta.get_nice_name

    class Meta:
        model = PresentationSet
        fields = ['PresentationRoom', 'AssessmentRoom', 'Track', 'Assessors', 'PresentationAssessors', 'DateTime']
        labels = {
            'PresentationRoom': "Presentation room",
            'AssessmentRoom': "Assessment room",
            'DateTime': "Start date/time",
            'PresentationAssessors': "Presentation Assessor (ESA)",
        }
        widgets = {
            'PresentationRoom': widgets.MetroSelect,
            'AssessmentRoom': widgets.MetroSelect,
            'Track': widgets.MetroSelect,
            'Assessors': widgets.MetroSelectMultiple,
            'PresentationAssessors': widgets.MetroSelectMultiple,
            'DateTime': widgets.MetroDateTimeInput,
        }

    def clean_DateTime(self):
        ts = get_timeslot()
        Phase = ts.timephases.get(Description=7)
        data = self.cleaned_data['DateTime']
        if data == '' or data is None:
            return data

        if data.date() < ts.Begin:  # allow presentations to be planned before phase 7, but not before timeslot.
             raise forms.ValidationError("The date is before the begin of this time slot. Please choose a later date")
        elif data.date() > Phase.End: # presentations cannot be planned after phase 7.
            raise forms.ValidationError("The date is after the presentations time phase. Please choose an earlier date")
        elif data.time() > time(hour=23):
            raise forms.ValidationError("The start time is after 23:00, which is too late")
        elif data.time() < time(hour=7):
            raise forms.ValidationError("The start time is before 7:00, which is too early")
        else:
            return data

    def save(self, commit=True):
        if commit:
            self.instance.PresentationOptions = get_timeslot().presentationoptions
            super().save(commit=True)
            self.instance.save()
        return self.instance


class PresentationRoomForm(forms.ModelForm):
    """
    A room in which presentations or assessments can be held.
    """

    class Meta:
        model = Room
        fields = ['Name', 'JoinLink']
        labels = {
            'Name': "Name of the room",
            'JoinLink': "Join link",
        }
        widgets = {
            'Name': widgets.MetroTextInput,
            'JoinLink': widgets.MetroURLInput,
        }


class MakePublicForm(forms.ModelForm):
    """
    ConfirmForm to make the presentationsplanning public in timephase 6.
    """

    class Meta:
        model = PresentationOptions
        fields = ["Public"]
        labels = {
            "Public": "Make calendar public visible"
        }
        widgets = {
            "Public": widgets.MetroCheckBox
        }
