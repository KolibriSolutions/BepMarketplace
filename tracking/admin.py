from django.contrib import admin
from .models import *

admin.site.register(ProposalStatusChange)
admin.site.register(UserLogin)
admin.site.register(ProposalTracking)
admin.site.register(ApplicationTracking)
admin.site.register(TelemetryKey)