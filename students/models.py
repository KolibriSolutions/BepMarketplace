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
    Proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name='distributions')
    Student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='distributions')
    Timeslot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name='distributions')
    Application = models.OneToOneField(Application, on_delete=models.CASCADE, blank=True, null=True, related_name='distributions')

    def TotalGrade(self):
        """
        Return total grade of student as not-rounded float
        :return:
        """
        return sum([r.Grade*r.Category.Weight for r in self.results.all()]) / 100

    def TotalGradeRounded(self):
        """
        Grade rounded to half points.
        :return:
        """
        return round(self.TotalGrade()*2, 0)/2

    def __str__(self):
        return self.Proposal.Title + " to " + self.Student.get_full_name() + " (" + self.Student.username + ")"