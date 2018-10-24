from django.contrib import admin

from .models import PresentationOptions, PresentationSet, PresentationTimeSlot, Room

admin.site.register(PresentationOptions)
admin.site.register(PresentationSet)
admin.site.register(PresentationTimeSlot)
admin.site.register(Room)
