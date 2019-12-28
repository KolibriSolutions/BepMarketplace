#  Bep Marketplace ELE
#  Copyright (c) 2016-2019 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.contrib import admin

from .models import CategoryResult, GradeCategory, GradeCategoryAspect, CategoryAspectResult


class GradeCategoryAdmin(admin.ModelAdmin):
    list_filter = ['TimeSlot']


class GradeCategoryAspectAdmin(admin.ModelAdmin):
    list_filter = ('Category', 'Category__TimeSlot')


class CategoryResultAdmin(admin.ModelAdmin):
    list_filter = ('Category', 'Category__TimeSlot')


class CategoryAspectResultAdmin(admin.ModelAdmin):
    list_filter = ('CategoryAspect__Category__TimeSlot', 'CategoryAspect__Category', 'CategoryResult')


admin.site.register(GradeCategoryAspect, GradeCategoryAspectAdmin)
admin.site.register(CategoryAspectResult, CategoryAspectResultAdmin)
admin.site.register(CategoryResult, CategoryResultAdmin)
admin.site.register(GradeCategory, GradeCategoryAdmin)
