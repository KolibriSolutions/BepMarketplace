#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.contrib import admin
from students.models import Distribution


class DistributionAdmin(admin.ModelAdmin):
    list_filter = ['TimeSlot']
    search_fields = ('Student__username', 'Student__last_name', 'Proposal__Title')


admin.site.register(Distribution, DistributionAdmin)
