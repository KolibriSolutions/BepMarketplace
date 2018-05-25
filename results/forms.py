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


class GradeCategoryForm(forms.ModelForm):
    """
    Form to edit a timeslot
    """

    class Meta:
        model = GradeCategory
        fields = ['Name', 'Weight']
        widgets = {
            'Name': widgets.MetroTextInput,
            'Weight': widgets.MetroNumberInput,
        }


class GradeCategoryAspectForm(forms.ModelForm):
    """
    Form to edit/create a timephase
    """

    class Meta:
        model = GradeCategoryAspect
        fields = ['Name', 'Description']
        widgets = {
            'Name': widgets.MetroTextInput,
            'Description': widgets.MetroTextInput,
        }


class MakeVisibleForm(forms.ModelForm):
    """
    Confirmform to make the presentationsplanning public in timephase 6.
    """

    class Meta:
        model = ResultOptions
        fields = ["Visible"]
        labels = {
            "Visible": "Make results visible for staff"
        }
        widgets = {
            "Visible": widgets.MetroCheckBox
        }
