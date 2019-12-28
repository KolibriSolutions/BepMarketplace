#  Bep Marketplace ELE
#  Copyright (c) 2016-2019 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.db import models

class AccessGrant(models.Model):
    LevelOptions = (
        (1, 'Type1'),
        (2, 'Type2')
    )

    Email = models.EmailField()
    Level = models.IntegerField(choices=LevelOptions, default=1)

    def __str__(self):
        return "{} for level {}".format(self.Email, self.Level)

