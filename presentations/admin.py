#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.contrib import admin

from .models import PresentationOptions, PresentationSet, PresentationTimeSlot, Room

admin.site.register(PresentationOptions)
admin.site.register(PresentationSet)
admin.site.register(PresentationTimeSlot)
admin.site.register(Room)
