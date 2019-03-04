from django.contrib import admin
from students.models import Distribution


class DistributionAdmin(admin.ModelAdmin):
    list_filter = ['TimeSlot']
    search_fields = ('Student__username', 'Student__last_name', 'Proposal__Title')


admin.site.register(Distribution, DistributionAdmin)
