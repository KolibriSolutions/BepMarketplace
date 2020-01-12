#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.contrib import admin

from .models import Application


class ApplicationAdmin(admin.ModelAdmin):
    readonly_fields = ('Timestamp',)
    list_filter = ['Proposal__TimeSlot']
    search_fields = ('Student__username', 'Student__last_name', 'Proposal__Title')


admin.site.register(Application, ApplicationAdmin)
