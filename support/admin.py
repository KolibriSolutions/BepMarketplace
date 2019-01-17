from django.contrib import admin

from .models import PublicFile, CapacityGroupAdministration


class PublicFileAdmin(admin.ModelAdmin):
    readonly_fields = ('Created', 'TimeStamp')
    list_filter = ['TimeSlot']


admin.site.register(CapacityGroupAdministration)
admin.site.register(PublicFile, PublicFileAdmin)
