#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.contrib import admin
from .models import *

class CanvasLoginAdmin(admin.ModelAdmin):
    search_fields = ['Subject__usermeta__Fullname', ]


admin.site.register(ProposalStatusChange)
admin.site.register(UserLogin)
admin.site.register(ProposalTracking)
admin.site.register(ApplicationTracking)
admin.site.register(TelemetryKey)
admin.site.register(CanvasLogin, CanvasLoginAdmin)
