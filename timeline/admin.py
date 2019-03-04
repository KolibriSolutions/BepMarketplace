from django.contrib import admin

from .models import TimePhase, TimeSlot


class TimePhaseAdmin(admin.ModelAdmin):
    list_filter = ['TimeSlot']


admin.site.register(TimePhase, TimePhaseAdmin)
admin.site.register(TimeSlot)
