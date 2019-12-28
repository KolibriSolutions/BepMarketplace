#  Bep Marketplace ELE
#  Copyright (c) 2016-2019 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django import forms
from django.conf import settings

# from general_view import get_timeslot
# from professionalskills.models import FileType, StudentFile
from templates import widgets
from .models import CategoryAspectResult, CategoryResult, GradeCategoryAspect, GradeCategory, ResultOptions


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


class GradeCategoryForm(forms.ModelForm):
    """
    Form to edit a gradecategory
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['File'].queryset = FileType.objects.filter(TimeSlot=get_timeslot())

    class Meta:
        model = GradeCategory
        fields = ['Name', 'Weight']#, 'File']
        widgets = {
            'Name': widgets.MetroTextInput,
            'Weight': widgets.MetroNumberInput,
            # 'File': widgets.MetroSelect,
        }


class CategoryResultForm(forms.ModelForm):
    """
    A students result to a grade category.
    """

    def __init__(self, *args, **kwargs):
        disabled = kwargs.pop('disabled', False)
        super().__init__(*args, **kwargs)
        self.fields['Grade'].disabled = disabled
        self.fields['Comments'].disabled = disabled
        self.fields['Comments'].widget.attrs['placeholder'] = "Please give some comments on the grade"
        self.fields['Grade'].widget.attrs = {'step': settings.CATEGORY_GRADE_QUANTIZATION, 'min': 0, 'max': 10}

    class Meta:
        model = CategoryResult
        fields = ['Grade', 'Comments']
        widgets = {
            'Grade': widgets.MetroNumberInput,
            'Comments': widgets.MetroMultiTextInput,
        }

#
# class CategoryResultFormFile(CategoryResultForm):
#     """
#     Inherits from CategoryResultForm, and gives the extra option to link specific files to a grade.
#     This can be used to grade files, as a student can upload multiple files for each filetype.
#     """
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # self.fields['Files'].queryset = StudentFile.objects.filter(Type=self.instance.Category.File, Distribution=self.instance.Distribution).distinct()
#
#     class Meta(CategoryResultForm.Meta):
#         fields = ['Grade', 'Comments']#, 'Files']
#         widgets = {
#             'Grade': widgets.MetroNumberInput,
#             'Comments': widgets.MetroMultiTextInput,
#             # 'Files': widgets.MetroSelectMultiple,
#         }


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
