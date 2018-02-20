from django import forms
from .models import FileType, StaffReponse, StudentGroup
from templates import widgets
from timeline.models import TimeSlot
from datetime import datetime
from django.db.models import Q

class FileTypeModelForm(forms.ModelForm):

    def save(self, commit=True):
        if self.errors:
            raise ValueError(
                "The %s could not be %s because the data didn't validate." % (
                    self.instance._meta.object_name,
                    'created' if self.instance._state.adding else 'changed',
                )
            )
        ts = TimeSlot.objects.filter(Q(Begin__lte=datetime.now()) & Q(End__gte=datetime.now()))[0]
        self.instance.TimeSlot = ts
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
            'CheckedBySupervisor' : widgets.MetroCheckBox,
        }
        labels = {
            'AllowedExtensions': 'Allowed file extensions',
            'CheckedBySupervisor': 'Supervisor check'
        }
        help_texts = {
            'CheckedBySupervisor': 'Check this box if the supervisor of the project has to review and grade this professional skill.'
        }


class ConfirmForm(forms.Form):
    confirm = forms.BooleanField(widget=widgets.MetroCheckBox, label='Confirm:')


class StaffReponseForm(forms.ModelForm):
    """
    A response from a staff member to a professionalskill file of a student.
    """
    class Meta:
        model = StaffReponse

        fields = [
            'Explanation',
            'Status',
        ]
        widgets = {
            'Explanation' : widgets.MetroTextInput,
            'Status' : widgets.MetroSelect,
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
            'PRV' : widgets.MetroSelect,
            'Number' : widgets.MetroNumberInputInteger,
            'Start' : widgets.MetroDateTimeInput,
            'Max' : widgets.MetroNumberInputInteger,
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


class StudentGroupChoice(forms.Form):
    """

    """
    Group = forms.ModelChoiceField(queryset=StudentGroup.objects.none() ,widget=widgets.MetroSelect)

    def __init__(self, *args, **kwargs):
        self.PRV = kwargs.pop('PRV')
        super().__init__(*args, **kwargs)
        self.fields['Group'].queryset = self.PRV.groups.all()