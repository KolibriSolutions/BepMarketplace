#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.contrib import admin
from django.shortcuts import reverse
from django.utils.html import format_html

from .models import Application


class ApplicationAdmin(admin.ModelAdmin):
    readonly_fields = ('Timestamp',)
    list_filter = ['Proposal__TimeSlot']
    search_fields = ('Student__username', 'Student__last_name', 'Proposal__Title')
    list_display = ['__str__', 'Student', 'detail_link', 'Priority']

    def detail_link(self, obj):
        url = reverse('proposals:details', args=[obj.Proposal.id])
        return format_html("<a href='{}'>{}</a>", url, obj.Proposal)


admin.site.register(Application, ApplicationAdmin)
