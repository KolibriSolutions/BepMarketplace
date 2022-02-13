#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django.utils.timezone import localtime

from general_model import clean_text, get_ext
from general_model import file_delete_default, metro_icon_default, filename_default, print_list
from students.models import Distribution
from timeline.models import TimeSlot
from datetime import datetime


class FileExtension(models.Model):
    Name = models.CharField(max_length=256)

    def __str__(self):
        return self.Name

    def clean(self):
        if self.Name[0] == '.':
            raise ValidationError("Please give extension without dot.")


class FileType(models.Model):
    """
    A type of file a student can handin. Like a planning, report or reflection.
    """
    Name = models.CharField(max_length=256)
    Deadline = models.DateField()
    TimeSlot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name='filetypes')
    Description = models.CharField(max_length=2056)
    AllowedExtensions = models.ManyToManyField(FileExtension)
    CheckedBySupervisor = models.BooleanField(default=True)

    # TODO check whether approval/grade of this file has to be in the prv staffresponse OR in the final grading at presentations
    # GradedInFinalGrade = models.BooleanField(default=False, help_text="Whether this file should be graded in the final grading process")
    # AvailableAtPresentation = models.BooleanField(default=False, help_text="Whether this file should be made available to the presentation assessors during the presentation.")

    def get_allowed_extensions(self):
        return list(self.AllowedExtensions.values_list('Name', flat=True))

    def __str__(self):
        return self.Name

    def clean(self):
        self.Name = clean_text(self.Name)
        self.Description = clean_text(self.Description)

    def deadline_passed(self):
        return self.Deadline < datetime.now().date()


class StudentFile(models.Model):
    """
    Model for a file that a student uploads. Linked to a distribution.
    """
    def make_upload_path(instance, filename):
        filenameNew = filename_default(filename)
        return 'dist_{0}/{1}'.format(instance.Distribution.pk, filenameNew)

    Caption = models.CharField(max_length=200, blank=True, null=True)
    OriginalName = models.CharField(max_length=200, blank=True, null=True)
    File = models.FileField(default=None, upload_to=make_upload_path)
    Distribution = models.ForeignKey(Distribution, on_delete=models.CASCADE, related_name='files')
    Type = models.ForeignKey(FileType, on_delete=models.PROTECT, related_name='files')
    TimeStamp = models.DateTimeField(auto_now=True)
    Created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return '{} - {}'.format(self.OriginalName, self.Caption)

    def metro_icon(self):
        return metro_icon_default(self)

    def save(self, *args, **kwargs):
        # remove old image if this is a changed image
        try:
            this_old = StudentFile.objects.get(id=self.id)
            if this_old.File != self.File:
                this_old.File.delete(save=False)
        except:  # new file object
            pass
        super(StudentFile, self).save(*args, **kwargs)

    def clean(self):
        # file extensions are cleaned in form.
        self.Caption = clean_text(self.Caption)

    def after_deadline(self):
        return self.TimeStamp.date() > self.Type.Deadline


class StudentGroup(models.Model):
    """
    A group of students for a professional skill
    """
    Number = models.IntegerField()
    PRV = models.ForeignKey(FileType, related_name='groups', on_delete=models.CASCADE)
    Start = models.DateTimeField()
    Members = models.ManyToManyField(User, related_name='studentgroups')
    Max = models.IntegerField(validators=[MinValueValidator(0)])

    def __str__(self):
        return 'Group {} at {} ({} of {} students)'.format(self.Number, localtime(self.Start).strftime("%a %d %b %H:%M"), self.Members.count(), self.Max)

    class Meta:
        ordering = ['PRV', 'Number']


@receiver(pre_delete, sender=StudentFile)
def student_file_delete(sender, instance, **kwargs):
    """
    Listener on studentfile, to remove the actual file when the object of the file is deleted.

    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    file_delete_default(sender, instance)


class StaffResponse(models.Model):
    """
    Response of a responsible staff member to a student uploaded file.
    """
    StatusOptions = (
        ("O", "Insufficient"),
        ("V", "Sufficient"),
        ("G", "Good")
    )
    StatusOptionsOsiris = {
        'O': 'ON',
        'V': 'VO',
        'G': 'GO',
    }

    File = models.OneToOneField(StudentFile, on_delete=models.CASCADE)
    TimestampCreated = models.DateTimeField(auto_now_add=True)
    TimestampLastEdited = models.DateTimeField(auto_now=True)
    Staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fileresponses')
    Explanation = models.CharField(max_length=2048, blank=True, null=True)
    Status = models.CharField(max_length=1, choices=StatusOptions)

    def __str__(self):
        return '{} of {}'.format(self.File.Type.Name, self.File.Distribution.Student.usermeta.get_nice_name())

    def clean(self):
        self.Explanation = clean_text(self.Explanation)

    def file_changed_after_grade(self):
        return self.TimestampLastEdited < self.File.TimeStamp


class StaffResponseFileAspect(models.Model):
    Name = models.CharField(max_length=255)
    Description = models.TextField()
    File = models.ForeignKey(FileType, on_delete=models.CASCADE, related_name='aspects')

    def clean(self):
        self.Description = clean_text(self.Description)
        self.Name = clean_text(self.Name)

    def __str__(self):
        return '{} to {}'.format(self.Name, self.File)


class StaffResponseFileAspectResult(models.Model):
    ResultOptions = (
        ("F", "Fail"),
        ("S", "Sufficient"),
        ("G", "Good"),
        ("VG", "Very Good"),
        ("E", "Excellent"),
    )

    Response = models.ForeignKey(StaffResponse, on_delete=models.CASCADE, related_name='aspects')
    Grade = models.CharField(max_length=2, choices=ResultOptions, blank=True, null=True)
    Aspect = models.ForeignKey(StaffResponseFileAspect, on_delete=models.CASCADE, related_name='results')

    def __str__(self):
        return '{} to file {}'.format(self.Aspect, self.Response.File)
