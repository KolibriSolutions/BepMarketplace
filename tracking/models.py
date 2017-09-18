from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from proposals.models import Proposal
from general_model import clean_text

class ProposalStatusChange(models.Model):
    Subject = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name="StatusChangeTracking")
    Timestamp = models.DateTimeField(auto_now_add=True)
    Actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="StatusChangeTracking")
    StatusFrom = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(4)],
                                     choices=Proposal.StatusOptions)
    StatusTo = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(4)],
                                     choices=Proposal.StatusOptions)
    Message = models.CharField(max_length=500, null=True, blank=True)

    def clean(self):
        self.Message = clean_text(self.Message)


class UserLogin(models.Model):
    Subject = models.ForeignKey(User, on_delete=models.CASCADE, related_name='logins')
    Timestamp = models.DateTimeField(auto_now_add=True)
    Page = models.CharField(max_length=1024)
    Twofactor = models.BooleanField(default=False)

    def __str__(self):
        return self.Subject.get_full_name() + "@" + self.Timestamp.strftime("%H:%M %d-%m-%Y")


class ProposalTracking(models.Model):
    Subject = models.OneToOneField(Proposal, on_delete=models.CASCADE, related_name='tracking')
    UniqueVisitors = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return str(self.Subject)


class ApplicationTracking(models.Model):
    typechoices = (
        ('a', 'applied'),
        ('r', 'retracted'),
    )

    Proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name='applicationtrackings')
    Student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applicationtrackings')
    Timestamp = models.DateTimeField(auto_now_add=True)
    Type = models.CharField(max_length=1, choices=typechoices)
