from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

from general_model import file_delete_default, metro_icon_default, filename_default
from students.models import Distribution
from timeline.models import TimeSlot
from general_model import clean_text


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
    TimeSlot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    Description = models.CharField(max_length=2056)
    AllowedExtensions = models.ManyToManyField(FileExtension)
    CheckedBySupervisor = models.BooleanField(default=True)

    def get_allowed_extensions(self):
        l = []
        for ext in self.AllowedExtensions.all():
            l.append(str(ext))
        return l

    def __str__(self):
        return self.Name


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
    Type = models.ForeignKey(FileType, on_delete=models.CASCADE, related_name='files')
    TimeStamp = models.DateTimeField(auto_now=True)
    Created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.OriginalName + " - " + self.Caption

    def metro_icon(self):
        return metro_icon_default(self)

    def save(self, *args, **kwargs):
        # remove old image if this is a changed image
        try:
            this_old = StudentFile.objects.get(id=self.id)
            if this_old.File != self.File:
                this_old.File.delete(save=False)
        except: # new image object
            pass
        super(StudentFile, self).save(*args, **kwargs)

    def clean(self):
        self.Caption = clean_text(self.Caption)


class StudentGroup(models.Model):
    """
    A group of students for a professionalskill
    """
    Number = models.IntegerField()
    PRV = models.ForeignKey(FileType, related_name='groups')
    Start = models.DateTimeField()
    Members = models.ManyToManyField(User, related_name='studentgroups')
    Max = models.IntegerField(validators=[MinValueValidator(0)])

    def __str__(self):
        return 'Group {} at {}, {}/{}'.format(self.Number, self.Start, self.Members.count(), self.Max)

    def clean(self):
        try:
            if self.Members.count() > self.Max:
                raise ValidationError('Group is full')
        except:
            pass
        if self.Number in [n.Number for n in self.PRV.groups.all()]:
            raise ValidationError('Group with that number already exists for this PRV')

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


class StaffReponse(models.Model):
    """
    Response of a responsible staff member to a student uploaded file.
    """
    StatusOptions = (
        ("O", "Insufficient"),
        ("V", "Sufficient"),
        ("G", "Good")
    )

    File = models.OneToOneField(StudentFile, on_delete=models.CASCADE)
    TimestampCreated = models.DateTimeField(auto_now_add=True)
    TimestampLastEdited = models.DateTimeField(auto_now=True)
    Staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fileresponses')
    Explanation = models.CharField(max_length=2048, blank=True, null=True)
    Status = models.CharField(max_length=1, choices=StatusOptions)

    def __str__(self):
        return '{} of {}'.format(self.File.Type.Name, self.File.Distribution.Student.get_full_name())

    def clean(self):
        self.Explanation = clean_text(self.Explanation)