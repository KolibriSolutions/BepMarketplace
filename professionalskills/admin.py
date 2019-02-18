from django.contrib import admin
from .models import FileType, FileExtension, StudentFile, StaffResponse, StudentGroup

admin.site.register(FileType)
admin.site.register(FileExtension)
admin.site.register(StudentFile)
admin.site.register(StaffResponse)
admin.site.register(StudentGroup)
