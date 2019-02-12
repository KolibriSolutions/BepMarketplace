from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from general_model import clean_text
from timeline.models import TimeSlot
from timeline.utils import get_timeslot_id


class Track(models.Model):
    """
    Stores the tracks for EE. Like SSS, CW, C&C en Automotive.
    Head is the professor that is the head of the track.
    """
    Name = models.CharField(max_length=255, unique=True)
    ShortName = models.CharField(max_length=10, unique=True)
    Head = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="tracks")

    def __str__(self):
        return str(self.ShortName)


class Broadcast(models.Model):
    """
    A message that is shown in the sidebar. Can be for everyone or only for one user (private).
    """
    Message = models.CharField(max_length=512)
    DateBegin = models.DateField(blank=True, null=True)
    DateEnd = models.DateField(blank=True, null=True)
    Private = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True,
                                related_name="private_broadcasts")

    def __str__(self):
        return self.Message

    def clean(self):
        self.Message = clean_text(self.Message)


class FeedbackReport(models.Model):
    """
    Feedback report as generated by a user. Viewable for superusers.
    """
    StatusChoices = (
        (1, "Open"),
        (2, "Confirmed"),
        (3, "Closed"),
    )

    Reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbackreports')
    Url = models.CharField(max_length=255)
    Feedback = models.CharField(max_length=1024)
    Timestamp = models.DateTimeField(auto_now_add=True)
    Status = models.IntegerField(choices=StatusChoices, validators=[MinValueValidator(1), MaxValueValidator(3)])

    def __str__(self):
        return "Report by " + self.Reporter.username + " Status: " + self.get_Status_display()

    def clean(self):
        self.Feedback = clean_text(self.Feedback)


class UserMeta(models.Model):
    """
    Meta for a user. Augmented user model. Overruled is true if some other fields should not be automatically updated
    using osiris.
    """
    User = models.OneToOneField(User, on_delete=models.CASCADE)
    SuppressStatusMails = models.BooleanField(default=False)
    Department = models.CharField(max_length=512, null=True, blank=True)
    Study = models.CharField(max_length=512, null=True, blank=True)
    Cohort = models.IntegerField(null=True, blank=True)
    Studentnumber = models.CharField(max_length=10, null=True, blank=True)
    Culture = models.CharField(max_length=32, null=True, blank=True)
    Initials = models.CharField(max_length=32, null=True, blank=True)
    Fullname = models.CharField(max_length=32, null=True, blank=True)
    ECTS = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(300)], default=0)
    EnrolledBEP = models.BooleanField(default=False)
    EnrolledExt = models.BooleanField(default=False)
    Overruled = models.BooleanField(default=False)
    TimeSlot = models.ManyToManyField(TimeSlot, default=get_timeslot_id, related_name='users')

    def __str__(self):
        return str(self.User)

    def get_nice_name(self):
        """
        Get a users full name with preposition

        :return:
        """
        if self.Fullname and '.' in self.Fullname and ',' in self.Fullname:
            last_name = self.Fullname.split(',')[0].strip()
            preposition = self.Fullname.split('.')[-1].strip()
            if preposition:
                return self.User.first_name + ' ' + preposition + ' ' + last_name
            return self.User.first_name + ' ' + last_name
        elif self.User.first_name or self.User.last_name:
            return self.User.get_full_name()
        else:
            return self.User.username  # users without name, should not happen.

    def get_nice_fullname(self):
        """
        Get fullname with fallback to normal name

        :return:
        """
        if self.Fullname and len(self.Fullname) > 2:
            return self.Fullname
        return self.get_nice_name()


class Term(models.Model):
    Text = models.TextField()

    def __str__(self):
        return "Term {}".format(self.id)


class UserAcceptedTerms(models.Model):
    User = models.OneToOneField(User, on_delete=models.CASCADE, related_name='termsaccepted')
    Stamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.User)
