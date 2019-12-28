#  Bep Marketplace ELE
#  Copyright (c) 2016-2019 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from datetime import timedelta

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth import get_user_model

from index.models import Track
from students.models import Distribution
from timeline.models import TimeSlot
from general_model import clean_text


class Room(models.Model):
    """
    A room to do things in.
    """
    Name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.Name

    def clean(self):
        self.Name = clean_text(self.Name)


class PresentationOptions(models.Model):
    """
    Global options and guidelines for all presentations. All presentations link back to this.
    """
    TimeSlot = models.OneToOneField(TimeSlot, on_delete=models.CASCADE, related_name="presentationoptions")
    PresentationDuration = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)], default=15)
    AssessmentDuration = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)], default=15)
    PresentationsBeforeAssessment = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)],
                                                        default=3)
    Public = models.BooleanField(default=False)

    def __str__(self):
        return "Presentation options for " + self.TimeSlot.__str__() + "."


class PresentationSet(models.Model):
    """
    A set of presentations. A set is a number of presentations in the same room for one track.
    """
    PresentationOptions = models.ForeignKey(PresentationOptions, on_delete=models.PROTECT,
                                            related_name="presentationsets")
    PresentationRoom = models.ForeignKey(Room, on_delete=models.PROTECT, related_name="presentationroom")
    AssessmentRoom = models.ForeignKey(Room, on_delete=models.PROTECT, related_name="assessmentroom")
    Track = models.ForeignKey(Track, on_delete=models.CASCADE, blank=True, null=True)
    Assessors = models.ManyToManyField(get_user_model(), blank=True)
    DateTime = models.DateTimeField()

    def __str__(self):
        return "Presentationset for " + self.PresentationOptions.TimeSlot.__str__() + " and track: " + self.Track.__str__()

    class Meta:
        ordering = ["DateTime"]


class PresentationTimeSlot(models.Model):
    """
    A presentation, assessment or break.
    """
    SlotTypes = (
        (1, 'Assessment'),
        (2, 'Break'),
        (3, 'Cancelled')
    )
    DateTime = models.DateTimeField()
    Presentations = models.ForeignKey(PresentationSet, on_delete=models.CASCADE, related_name="timeslots")
    Distribution = models.OneToOneField(Distribution, on_delete=models.CASCADE, related_name="presentationtimeslot",
                                        blank=True, null=True, default=None)
    CustomType = models.IntegerField(choices=SlotTypes, default=0, null=True)
    CustomDuration = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)], blank=True,
                                         null=True, default=None)

    class Meta:
        ordering = ['DateTime']

    def Duration(self):
        """
        Duration of this timeslot

        :return:
        """
        if self.CustomDuration:
            return self.CustomDuration
        elif self.CustomType == 1:
            return self.Presentations.PresentationOptions.AssessmentDuration
        else:
            return self.Presentations.PresentationOptions.PresentationDuration

    def DateTimeEnd(self):
        """
        End time of this timeslot
        :return:
        """
        return self.DateTime + timedelta(minutes=self.Duration())

    def __str__(self):
        return str(self.Distribution) + " @ " + str(self.DateTime)
