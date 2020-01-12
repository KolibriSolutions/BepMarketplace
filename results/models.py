#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.aggregates import Sum

from general_model import clean_text
# from index.models import Track
# from professionalskills.models import FileType, StudentFile
from students.models import Distribution
from timeline.models import TimeSlot
from timeline.utils import get_timeslot_id
from .utils import quantize_number


class ResultOptions(models.Model):
    """
    Global options and guidelines for all results
    """
    TimeSlot = models.OneToOneField(TimeSlot, on_delete=models.PROTECT, related_name="resultoptions")
    Visible = models.BooleanField(default=False)

    def __str__(self):
        return "Result options for {}.".format(self.TimeSlot)


class GradeCategory(models.Model):
    """
    A category of a final grade. A student get a subgrade for each category. A category has sub aspects.
    """
    Weight = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    Name = models.CharField(max_length=255)
    TimeSlot = models.ForeignKey(TimeSlot, default=get_timeslot_id, related_name='gradecategories', blank=False,
                                 on_delete=models.PROTECT)
    # File = models.ForeignKey(FileType, related_name='results', blank=True, null=True, on_delete=models.CASCADE, help_text='If this category is to grade a file or professional skill, select the file type here.')  # replaced by PRV grade system.

    class Meta:
        ordering = ["-Weight", "Name"]

    def __str__(self):
        # if self.File:
        #     return '{} for {} ({}%)'.format(self.Name, self.File, self.Weight)
        return '{} ({}%)'.format(self.Name, self.Weight)

    def clean(self):
        ws = GradeCategory.objects.filter(TimeSlot=get_timeslot_id())
        if self.id:
            ws = ws.exclude(id=self.id)
        try:
            w = ws.aggregate(Sum('Weight'))['Weight__sum'] + self.Weight
        except:
            w = self.Weight
        if w > 100:
            raise ValidationError("Total weight of categories should be below 100%, it is now {}%!".format(w))
        self.Name = clean_text(self.Name)


class CategoryResult(models.Model):
    """
    The score of a student on a particular grade category.
    """
    Distribution = models.ForeignKey(Distribution, on_delete=models.CASCADE, related_name='results')
    Category = models.ForeignKey(GradeCategory, on_delete=models.PROTECT, related_name='results')
    Grade = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(10)], default=0.0)
    Comments = models.TextField(blank=True, null=True)
    Final = models.BooleanField(default=False)
    # Files = models.ManyToManyField(StudentFile, related_name='results', blank=True)

    def __str__(self):
        return '{} to {} grade: {}'.format(self.Category.Name, self.Distribution.__str__(), self.Grade)

    def is_valid(self):
        """
        Check if comment field is filled and all aspects have a grade.

        :return:
        """
        return self.Comments and self.aspectresults.count() == self.Category.aspects.count() and all([a.Grade for a in self.aspectresults.all()])

    class Meta:
        ordering = ["Category"]

    def clean(self):
        self.Comments = clean_text(self.Comments)
        self.Grade = quantize_number(self.Grade, base=settings.CATEGORY_GRADE_QUANTIZATION)  # rounds grade to step from settings.


class GradeCategoryAspect(models.Model):
    """
    A aspect of a grade category. A subgrade to explain the grade of the category.
    """
    Category = models.ForeignKey(GradeCategory, on_delete=models.CASCADE, related_name='aspects')
    Name = models.CharField(max_length=255)
    Description = models.TextField()

    class Meta:
        ordering = ['Category', 'Name']

    def __str__(self):
        return '{} in {}'.format(self.Name, self.Category)

    def clean(self):
        self.Description = clean_text(self.Description)
        self.Name = clean_text(self.Name)


class CategoryAspectResult(models.Model):
    """
    The score of a student to a particular aspect of a category. Linked to the students categoryresult.
    """
    ResultOptions = (
        ("F", "Fail"),
        ("S", "Sufficient"),
        ("G", "Good"),
        ("VG", "Very Good"),
        ("E", "Excellent"),
    )

    CategoryAspect = models.ForeignKey(GradeCategoryAspect, on_delete=models.PROTECT, related_name='results')
    Grade = models.CharField(max_length=2, choices=ResultOptions, blank=True, null=True)
    CategoryResult = models.ForeignKey(CategoryResult, on_delete=models.CASCADE, related_name='aspectresults')

    class Meta:
        ordering = ['CategoryAspect']  # inherit sorting

    def __str__(self):
        return '{} to {} grade: {}'.format(self.CategoryAspect.Name, self.CategoryResult.Distribution.__str__(), self.Grade)
