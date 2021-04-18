#  Bep Marketplace ELE
#  Copyright (c) 2016-2021 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.contrib import admin
from .models import FileType, FileExtension, StudentFile, StaffResponse, StudentGroup, StaffResponseFileAspect, StaffResponseFileAspectResult


class StudentFileAdmin(admin.ModelAdmin):
    list_filter = ['Distribution__TimeSlot', 'Type']
    list_display = ['__str__', 'Distribution']
    search_fields = ('Distribution__Student__username', 'Distribution__Student__last_name')
    readonly_fields = ('TimeStamp', 'Created',)


class FileTypeAdmin(admin.ModelAdmin):
    list_filter = ['TimeSlot', 'AllowedExtensions']
    list_display = ['__str__', 'TimeSlot', 'Deadline', 'CheckedBySupervisor']
    # search_fields = ('Distribution__Student__username', 'Distribution__Student__last_name')


class StaffResponseAdmin(admin.ModelAdmin):
    list_filter = ['File__Distribution__TimeSlot', 'File__Type']
    list_display = ['__str__', 'File']
    readonly_fields = ('TimestampCreated', 'TimestampLastEdited',)


class StaffResponseFileAspectAdmin(admin.ModelAdmin):
    list_filter = ['File', 'File__TimeSlot']
    list_display = ['__str__', 'File']


admin.site.register(FileType, FileTypeAdmin)
admin.site.register(FileExtension)
admin.site.register(StudentFile, StudentFileAdmin)
admin.site.register(StaffResponse, StaffResponseAdmin)
admin.site.register(StudentGroup)
admin.site.register(StaffResponseFileAspect, StaffResponseFileAspectAdmin)
admin.site.register(StaffResponseFileAspectResult)
