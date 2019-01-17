import logging
from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver

from general_model import GroupOptions, file_delete_default, filename_default, clean_text, get_ext, print_list
from index.models import Track
from timeline.models import TimeSlot
from timeline.utils import get_timeslot

logger = logging.getLogger('django')


class Proposal(models.Model):
    """
    Model for a project.
    """
    StatusOptions = (
        (1, 'Draft, awaiting completion by type 2 (assistant)'),
        (2, 'Draft, awaiting approval by type 1 (professor)'),
        (3, 'On hold, awaiting approval track head'),
        (4, 'Active proposal'),
    )

    Title = models.CharField(max_length=100)
    ResponsibleStaff = models.ForeignKey(User, on_delete=models.PROTECT, related_name='proposalsresponsible')
    Assistants = models.ManyToManyField(User, related_name='proposals', blank=True)
    Group = models.CharField(max_length=3, choices=GroupOptions)
    NumstudentsMin = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    NumstudentsMax = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    GeneralDescription = models.TextField()
    StudentsTaskDescription = models.TextField()
    ExtensionDescription = models.TextField(null=True, blank=True)
    Track = models.ForeignKey(Track, on_delete=models.PROTECT)
    Private = models.ManyToManyField(User, blank=True, related_name='personal_proposal')
    Status = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(4)],
                                 choices=StatusOptions)
    TimeSlot = models.ForeignKey(TimeSlot, related_name='proposals', null=True, blank=True, on_delete=models.PROTECT, help_text='The year this proposal is used. Set to "--" to save the proposal for a future time. Only the proposals of the current timeslot can be used in the current timeslot.')
    TimeStamp = models.DateTimeField(auto_now=True, null=True)
    Created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.Title + " from " + self.ResponsibleStaff.username

    def num_distributions(self):
        return int(self.distributions.count())

    def prevyear(self):
        """
        Whether this proposal is from a previous timeslot. Proposals without timeslot are future proposals.
        :return:
        """
        if self.TimeSlot:
            if self.TimeSlot.End < datetime.now().date():
                return True
        return False

    def nextyear(self):
        """
        Whether this proposal is for the future. Proposals without timeslot are future proposals.
        :return:
        """
        if not self.TimeSlot:  # anywhere in the future
            return True
        elif self.TimeSlot.Begin > datetime.now().date():
            return True
        else:
            return False

    def curyear(self):
        if self.TimeSlot:
            return self.TimeSlot == get_timeslot()
        else:  # future proposal
            return False

    def clean(self):
        self.Title = clean_text(self.Title)
        self.GeneralDescription = clean_text(self.GeneralDescription)
        self.StudentsTaskDescription = clean_text(self.StudentsTaskDescription)

        min_std = self.NumstudentsMin
        max_std = self.NumstudentsMax
        if min_std and max_std:
            if min_std > max_std:
                raise ValidationError("Minimum number of students cannot be higher than maximum.")
        else:
            raise ValidationError("Min or max number of students cannot be empty")


class ProposalFile(models.Model):
    """
    Abstract base class for any object attached to a project. Used for images and attachments.
    """

    def make_upload_path(instance, filename):
        filename_new = filename_default(filename)
        return 'proposal_{0}/{1}'.format(instance.Proposal.pk, filename_new)

    Caption = models.CharField(max_length=200, blank=True, null=True)
    OriginalName = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.Proposal.Title + ' ' + self.Caption

    def clean(self):
        self.Caption = clean_text(self.Caption)


class ProposalImage(ProposalFile):
    Proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name='images')
    File = models.ImageField(default=None, upload_to=ProposalFile.make_upload_path)

    def save(self, *args, **kwargs):
        # remove old image if this is a changed image
        try:
            this_old = ProposalImage.objects.get(id=self.id)
            if this_old.File != self.File:
                this_old.File.delete(save=False)
        except ProposalImage.DoesNotExist:  # new image object
            pass
        super(ProposalImage, self).save(*args, **kwargs)

    def clean(self):
        if self.File:
            if get_ext(self.File.name) not in settings.ALLOWED_PROJECT_IMAGES:
                raise ValidationError(
                    'This file type is not allowed. Allowed types: ' + print_list(settings.ALLOWED_PROJECT_IMAGES))


class ProposalAttachment(ProposalFile):
    Proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name='attachments')
    File = models.FileField(default=None, upload_to=ProposalFile.make_upload_path)

    def save(self, *args, **kwargs):
        # remove old attachement if the attachement changed
        try:
            this_old = ProposalAttachment.objects.get(id=self.id)
            if this_old.File != self.File:
                this_old.File.delete(save=False)
        except ProposalAttachment.DoesNotExist:  # new file object
            pass
        super(ProposalAttachment, self).save(*args, **kwargs)

    def clean(self):
        if self.File:
            if get_ext(self.File.name) not in settings.ALLOWED_PROJECT_ATTACHMENTS:
                raise ValidationError(
                    'This file type is not allowed. Allowed types: '
                    + print_list(settings.ALLOWED_PROJECT_ATTACHMENTS))


class Favorite(models.Model):
    """
    users favourite a project.
    """
    Project = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name='favorites')
    User = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    Timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.User.get_username() + " to " + self.Project.__str__()

    # class Meta:
    #     ordering = ["User"]

    def clean(self):
        if self.User.favorites.filter(Project=self.Project).exists():
            raise ValidationError("You already favorite this project")


# delete image if ProposalImage Object is removed
@receiver(pre_delete, sender=[ProposalAttachment, ProposalImage])
def proposal_file_delete(sender, instance, **kwargs):
    file_delete_default(sender, instance)
