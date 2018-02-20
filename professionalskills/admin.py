from django.contrib import admin
from .models import FileType, FileExtension, StudentFile, StaffReponse, StudentGroup

admin.site.register(FileType)
admin.site.register(FileExtension)
admin.site.register(StudentFile)
admin.site.register(StaffReponse)
admin.site.register(StudentGroup)