#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.contrib import admin

from .models import AccessGrant, OsirisDataFile

admin.site.register(AccessGrant)
admin.site.register(OsirisDataFile)
