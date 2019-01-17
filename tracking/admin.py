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