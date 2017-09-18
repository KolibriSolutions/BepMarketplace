from django.contrib import admin
from .models import PublicFile, CapacityGroupAdministration

admin.site.register(CapacityGroupAdministration)
admin.site.register(PublicFile)