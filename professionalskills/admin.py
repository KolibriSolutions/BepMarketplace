from django.contrib import admin
from .models import FileType, FileExtension, StudentFile, StaffResponse, StudentGroup, StaffResponseFileAspect, StaffResponseFileAspectResult

admin.site.register(FileType)
admin.site.register(FileExtension)
admin.site.register(StudentFile)
admin.site.register(StaffResponse)
admin.site.register(StudentGroup)
admin.site.register(StaffResponseFileAspect)
admin.site.register(StaffResponseFileAspectResult)