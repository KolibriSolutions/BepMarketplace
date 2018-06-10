from django import forms

from templates import widgets
from .models import CategoryAspectResult, CategoryResult, GradeCategoryAspect, GradeCategory, ResultOptions


class CategoryResultForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        disabled = kwargs.pop('disabled', False)
        super().__init__(*args, **kwargs)
        self.fields['Grade'].disabled = disabled
        self.fields['Comments'].disabled = disabled

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
    def __init__(self, *args, **kwargs):
        disabled = kwargs.pop('disabled', False)
        super().__init__(*args, **kwargs)
        self.fields['Grade'].disabled = disabled

    class Meta:
        model = CategoryAspectResult
        fields = ['Grade']
        widgets = {
            'Grade': widgets.MetroSelectRadioTable
        }


class GradeCategoryForm(forms.ModelForm):
    """
    Form to edit a gradecategory
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
    Form to edit/create a category aspect.
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
    Confirmform to make the grading forms visible
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
