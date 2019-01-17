from django.contrib import admin

from .models import Application


class ApplicationAdmin(admin.ModelAdmin):
    readonly_fields = ('Timestamp',)
    list_filter = ['Proposal__TimeSlot']
    search_fields = ('Student__username', 'Student__last_name', 'Proposal__Title')


admin.site.register(Application, ApplicationAdmin)
