from django import forms

from templates import widgets
from .models import *


class CategoryResultForm(forms.ModelForm):
    class Meta:
        model = CategoryResult
        fields = ['Grade', 'Comments']
        widgets = {
            'Grade': widgets.MetroNumberInputInteger,
            'Comments': widgets.MetroMultiTextInput,
        }

    def clean_Grade(self):
        """
        Grades are rounded to integers.

        :return: rounded grade.
        """
        return round(self.cleaned_data['Grade'], 0)


class AspectResultForm(forms.ModelForm):
    class Meta:
        model = CategoryAspectResult
        fields = ['Grade']
        widgets = {
            'Grade': widgets.MetroSelect
        }
