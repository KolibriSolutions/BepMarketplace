from django import forms
from .models import FileType, StaffReponse
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
            'Deadline': widgets.MetroTextInput,
            'Description': widgets.MetroTextInput,
            'AllowedExtensions': widgets.MetroSelectMultiple,
            'CheckedBySupervisor' : widgets.MetroCheckBox,
        }

class ConfirmForm(forms.Form):
    confirm = forms.BooleanField(widget=widgets.MetroCheckBox, label='Confirm:')

class StaffReponseForm(forms.ModelForm):

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