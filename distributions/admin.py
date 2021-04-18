#  Bep Marketplace ELE
#  Copyright (c) 2016-2021 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.contrib import admin
from students.models import Distribution
from django.utils.html import format_html
from django.shortcuts import reverse


class DistributionAdmin(admin.ModelAdmin):
    list_filter = ['Proposal__TimeSlot']
    search_fields = ('Student__username', 'Student__last_name', 'Proposal__Title')
    list_display = ['__str__', 'Student', 'detail_link']

    def detail_link(self, obj):
        url = reverse('proposals:details', args=[obj.Proposal.id])
        return format_html("<a href='{}'>{}</a>", url, obj.Proposal)


admin.site.register(Distribution, DistributionAdmin)
6