#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from proposals.models import Proposal
from timeline.models import TimeSlot
from django.conf import settings


class Application(models.Model):
    """
    A student's application to a proposal.
    """
    Priority = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(settings.MAX_NUM_APPLICATIONS)])
    Proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name='applications')
    Student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    Timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.Student.get_username() + " to " + self.Proposal.__str__()

    class Meta:
        ordering = ["Priority"]


class Distribution(models.Model):
    """A student distributed to a proposal.x"""
    Proposal = models.ForeignKey(Proposal, on_delete=models.PROTECT, related_name='distributions')
    Student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='distributions', limit_choices_to={'groups':None})
    TimeSlot = models.ForeignKey(TimeSlot, on_delete=models.PROTECT, related_name='distributions')
    Application = models.OneToOneField(Application, on_delete=models.SET_NULL, blank=True, null=True, related_name='distributions')

    def TotalGrade(self):
        """
        Return total grade of student as not-rounded float
        :return:
        """
        return sum([r.Grade * r.Category.Weight for r in self.results.all()]) / 100

    def TotalGradeRounded(self):
        """
        Grade rounded to half points.
        :return:
        """
        return round(self.TotalGrade() * 2, 0) / 2

    def missing_files(self):
        return self.TimeSlot.filetypes.exclude(pk__in=self.files.values_list('Type', flat=True))

    def missing_file_gradings(self):
        return self.files.filter(Type__CheckedBySupervisor=True).filter(staffresponse__isnull=True)

    def __str__(self):
        return self.Proposal.Title + " to " + self.Student.usermeta.get_nice_name() + " (" + self.Student.username + ")"
