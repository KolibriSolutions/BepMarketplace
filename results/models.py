from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from general_model import clean_text
from timeline.utils import get_timeslot_id
from index.models import Track
from students.models import Distribution
from timeline.models import TimeSlot


class GradeCategory(models.Model):
    """
    A category of a final grade. A student get a subgrade for each category. A category has sub aspects.
    """
    Weight = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    Name =  models.CharField(max_length=255, unique=True)
    TimeSlot = models.ForeignKey(TimeSlot, default=get_timeslot_id, related_name='gradecategories', blank=False,
                                 on_delete=models.PROTECT)
    class Meta:
        ordering = ["-Weight", "Name"]

    def __str__(self):
        return self.Name + " (" + str(self.Weight) + "%)"


class CategoryResult(models.Model):
    """
    The score of a student on a particular grade category.
    """
    Distribution = models.ForeignKey(Distribution, on_delete=models.CASCADE, related_name='results')
    Category = models.ForeignKey(GradeCategory, on_delete=models.CASCADE, related_name='results')
    Grade = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(10)], default=0.0)
    Comments = models.TextField()
    Final = models.BooleanField(default=False)

    def __str__(self):
        return self.Category.Name + " to " + self.Distribution.__str__() + " grade: " + str(self.Grade)

    def is_valid(self):
        return self.aspectresults.count() == self.Category.aspects.count()

    class Meta:
        ordering = ["Category"]

    def clean(self):
        self.Comments = clean_text(self.Comments)


class GradeCategoryAspect(models.Model):
    """
    A aspect of a grade category. A subgrade to explain the grade of the category.
    """
    Category = models.ForeignKey(GradeCategory, on_delete=models.CASCADE, related_name='aspects')
    Name = models.CharField(max_length=255, unique=True)
    Description = models.TextField()

    def __str__(self):
        return self.Name + " in " + str(self.Category)

    def clean(self):
        self.Description = clean_text(self.Description)
        self.Name = clean_text(self.Name)


class CategoryAspectResult(models.Model):
    """
    The score of a student to a particular aspect of a category. Linked to the students categoryresult.
    """
    ResultOptions = (
        ("E", "Excellent"),
        ("VG", "Very Good"),
        ("G", "Good"),
        ("S", "Sufficient"),
        ("F", "Fail"),
    )

    CategoryAspect = models.ForeignKey(GradeCategoryAspect, on_delete=models.CASCADE, related_name='results')
    Grade = models.CharField(max_length=2, choices=ResultOptions)
    CategoryResult = models.ForeignKey(CategoryResult, on_delete=models.CASCADE, related_name='aspectresults')

    def __str__(self):
        return self.CategoryAspect.Name + " to " + self.CategoryResult.Distribution.__str__() + " grade: " + self.Grade