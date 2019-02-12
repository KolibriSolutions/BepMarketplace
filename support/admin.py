from django.contrib import admin

from .models import PublicFile, CapacityGroup, GroupAdministratorThrough


class PublicFileAdmin(admin.ModelAdmin):
    readonly_fields = ('Created', 'TimeStamp')
    list_filter = ['TimeSlot']


admin.site.register(PublicFile, PublicFileAdmin)
admin.site.register(CapacityGroup)
admin.site.register(GroupAdministratorThrough)
