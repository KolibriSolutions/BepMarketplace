#  Bep Marketplace ELE
#  Copyright (c) 2016-2019 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.contrib import admin

from .models import Proposal, ProposalImage, ProposalAttachment, Favorite
from django.shortcuts import reverse
from django.utils.html import format_html


class ProposalAdmin(admin.ModelAdmin):
    search_fields = ['Title', ]
    list_filter = ('Track', 'Status', 'TimeSlot', 'Group')
    list_display = ['Title', 'ResponsibleStaff', 'Status', 'detail_link']

    def detail_link(self, obj):
        url = reverse('proposals:details', args=[obj.id])
        return format_html("<a href='{}'>{}</a>", url, obj)


class FavoriteAdmin(admin.ModelAdmin):
    search_fields = ['Project', 'User']
    list_filter = ('Project__Track', 'Project__Status', 'Project__TimeSlot', 'Project__Group')
    list_display = ['__str__', 'detail_link', 'User']

    def detail_link(self, obj):
        url = reverse('proposals:details', args=[obj.Project.id])
        return format_html("<a href='{}'>{}</a>", url, obj.Project)


class ProposalFileAdmin(admin.ModelAdmin):
    search_fields = ['Proposal__Title', 'Caption']


admin.site.register(Proposal, ProposalAdmin)
admin.site.register(ProposalImage, ProposalFileAdmin)
admin.site.register(ProposalAttachment, ProposalFileAdmin)
admin.site.register(Favorite, FavoriteAdmin)
