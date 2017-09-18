from django.contrib.auth.models import Group, User
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver

from general_model import file_delete_default, filename_default, clean_text, get_timeslot_id
from index.models import Track
from timeline.models import TimeSlot
from general_model import GroupOptions

class Proposal(models.Model):

    StatusOptions = (
        (1, "Draft, awaiting completion by type 2 (assistant)"),
        (2, "Draft, awaiting approval by type 1 (professor)"),
        (3, "Final draft, awaiting approval track head"),
        (4, "Active proposal"),
    )

    Title = models.CharField(max_length=100, unique=True)
    ResponsibleStaff = models.ForeignKey(User, on_delete=models.PROTECT, related_name='proposalsresponsible')
    Group = models.CharField(max_length=3, choices=GroupOptions)
    NumstudentsMin = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    NumstudentsMax = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    GeneralDescription = models.TextField()
    StudentsTaskDescription = models.TextField()
    ECTS = models.IntegerField(choices=((10, 10), (15, 15)))
    Track = models.ForeignKey(Track, on_delete=models.PROTECT)
    Private = models.ManyToManyField(User, blank=True, related_name='personal_proposal')
    Assistants = models.ManyToManyField(User, related_name='proposals', blank=True)
    Status = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(4)], choices=StatusOptions)
    TimeSlot = models.ForeignKey(TimeSlot, default=get_timeslot_id, related_name='proposals', blank=False, on_delete=models.PROTECT)

    def __str__(self):
        return self.Title + " from " + self.ResponsibleStaff.username

    def nDistributions(self):
        return int(self.distributions.count())

    def clean(self):
        self.Title = clean_text(self.Title)
        self.GeneralDescription = clean_text(self.GeneralDescription)
        self.StudentsTaskDescription = clean_text(self.StudentsTaskDescription)


class ProposalFile(models.Model):
    def make_upload_path(instance, filename):
        filenameNew =  filename_default(filename)
        return 'proposal_{0}/{1}'.format(instance.Proposal.pk,filenameNew)
    Caption = models.CharField(max_length=200, blank=True, null=True)
    OriginalName = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.Proposal.Title + " " + self.Caption

    def save(self, *args, **kwargs):
        self.OriginalName = self.File.name
        super(ProposalFile, self).save(*args, **kwargs)

    def clean(self):
        self.Caption = clean_text(self.Caption)


class ProposalImage(ProposalFile):
    Proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name='images')
    File = models.ImageField(default=None, upload_to=ProposalFile.make_upload_path)

    def save(self, *args, **kwargs):
        #remove old image if this is a changed image
        try:
            this_old = ProposalImage.objects.get(id=self.id)
            if this_old.File != self.File:
                this_old.File.delete()
        except: #new image object
            pass
        super(ProposalImage, self).save(*args, **kwargs)


class ProposalAttachment(ProposalFile):
    Proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name='attachments')
    File = models.FileField(default=None, upload_to=ProposalFile.make_upload_path)

    def save(self, *args, **kwargs):
        #remove old attachement if the attachement changed
        try:
            this_old = ProposalAttachment.objects.get(id=self.id)
            if this_old.File != self.File:
                this_old.File.delete()
        except:  # new image object
            pass
        super(ProposalAttachment, self).save(*args, **kwargs)


# delete image if ProposalImage Object is removed
@receiver(pre_delete, sender=[ProposalAttachment, ProposalImage])
def proposal_file_delete(sender, instance, **kwargs):
    file_delete_default(sender, instance)