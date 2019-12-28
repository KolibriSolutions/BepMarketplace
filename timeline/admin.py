#  Bep Marketplace ELE
#  Copyright (c) 2016-2019 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.contrib import admin

from .models import TimePhase, TimeSlot


class TimePhaseAdmin(admin.ModelAdmin):
    list_filter = ['TimeSlot']


admin.site.register(TimePhase, TimePhaseAdmin)
admin.site.register(TimeSlot)
