from django.contrib import admin
from .models import CategoryResult, GradeCategory, GradeCategoryAspect, CategoryAspectResult

admin.site.register(GradeCategoryAspect)
admin.site.register(CategoryAspectResult)
admin.site.register(CategoryResult)
admin.site.register(GradeCategory)