#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.db import models

from general_model import filename_default
from timeline.models import TimeSlot
from timeline.utils import get_timeslot_id


class AccessGrant(models.Model):
    LevelOptions = (
        (1, 'Type1'),
        (2, 'Type2')
    )

    Email = models.EmailField()
    Level = models.IntegerField(choices=LevelOptions, default=1)

    def __str__(self):
        return "{} for level {}".format(self.Email, self.Level)


class OsirisDataFile(models.Model):
    def make_upload_path(instance, filename):
        filename_new = filename_default(filename)
        return 'OsirisDataFile/{0}-{1}.csv'.format(instance.TimeSlot, filename_new)

    TimeSlot = models.ForeignKey(TimeSlot, default=get_timeslot_id, on_delete=models.PROTECT)
    File = models.FileField()
    TimeStamp = models.DateTimeField(auto_now=True, null=True)
    Created = models.DateTimeField(auto_now_add=True, null=True)

