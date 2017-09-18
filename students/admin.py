from django.contrib import admin
from .models import Application

class ApplicationAdmin(admin.ModelAdmin):
    readonly_fields = ('Timestamp',)

admin.site.register(Application, ApplicationAdmin)
