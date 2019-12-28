#  Bep Marketplace ELE
#  Copyright (c) 2016-2019 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.contrib import admin

from .models import PublicFile, CapacityGroup, GroupAdministratorThrough, MailTemplate, Mailing


class PublicFileAdmin(admin.ModelAdmin):
    readonly_fields = ('Created', 'TimeStamp')
    list_filter = ['TimeSlot']


admin.site.register(PublicFile, PublicFileAdmin)
admin.site.register(CapacityGroup)
admin.site.register(GroupAdministratorThrough)
admin.site.register(MailTemplate)
admin.site.register(Mailing)
