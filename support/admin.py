from django.contrib import admin
from .models import PublicFile, CapacityGroupAdministration


class PublicFileAdmin(admin.ModelAdmin):
    readonly_fields = ('Created', 'TimeStamp')

admin.site.register(CapacityGroupAdministration)
admin.site.register(PublicFile, PublicFileAdmin)