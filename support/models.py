from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django.forms import ValidationError

from general_model import GroupOptions, print_list, get_ext
from general_model import file_delete_default, metro_icon_default, filename_default, clean_text
from proposals.utils import get_all_proposals
from timeline.models import TimeSlot
from timeline.utils import get_timeslot, get_timeslot_id


class CapacityGroupAdministration(models.Model):
    """
    Model to set the administrative users for a capacity group.
    """
    Group = models.CharField(max_length=3, choices=GroupOptions)
    Members = models.ManyToManyField(User, related_name='groupadministrations', blank=True)

    def Proposals(self):
        return get_all_proposals().filter(Group=self.Group)

    def __str__(self):
        return self.Group + " Administration"


class PublicFile(models.Model):
    """
    Public file. Support staff can upload these and the files are shown for each user on the frontpage.
    """

    def make_upload_path(instance, filename):
        """
        Upload path for a public file. Stored in /media/public_files/{timeslot-id}/{uuid.ext}

        :param filename:
        :return:
        """
        filename_new = filename_default(filename)
        return 'public_files/{0}/{1}'.format(str(get_timeslot().id), filename_new)

    Caption = models.CharField(max_length=200, blank=True, null=True)
    OriginalName = models.CharField(max_length=200, blank=True, null=True)
    File = models.FileField(default=None, upload_to=make_upload_path)
    TimeSlot = models.ForeignKey(TimeSlot, default=get_timeslot_id, on_delete=models.CASCADE,
                                 related_name='public_files')
    User = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    TimeStamp = models.DateTimeField(auto_now=True, blank=True, null=True)
    Created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def metro_icon(self):
        return metro_icon_default(self)

    def __str__(self):
        return str(self.OriginalName) + " - " + str(self.Caption)

    def save(self, *args, **kwargs):
        # remove old image if this is a changed image
        try:
            this_old = PublicFile.objects.get(id=self.id)
            if this_old.File != self.File:
                this_old.File.delete(save=False)
        except:  # new image object
            pass
        super(PublicFile, self).save(*args, **kwargs)

    def clean(self):
        self.Caption = clean_text(self.Caption)
        if self.File:
            if get_ext(self.File.name) not in settings.ALLOWED_PUBLIC_FILES:
                raise ValidationError(
                    'This file type is not allowed. Allowed types: ' + print_list(settings.ALLOWED_PUBLIC_FILES))


@receiver(pre_delete, sender=PublicFile)
def public_file_delete(sender, instance, **kwargs):
    """
    Delete actual file if publicfile Object is removed

    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    file_delete_default(sender, instance)
