#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.contrib import admin
from django.shortcuts import reverse
from django.utils.html import format_html

from .models import Track, Broadcast, FeedbackReport, UserMeta, Term, UserAcceptedTerms


class UserMetaAdmin(admin.ModelAdmin):
    search_fields = ['User__username', 'Fullname', 'User__email', 'User__username']
    list_filter = ('User__groups', 'Cohort', 'EnrolledBEP', 'EnrolledExt')
    list_display = ['Fullname', 'User', 'user_link']

    def user_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.User.id])
        return format_html("<a href='{}'>{}</a>", url, obj)


class UserAcceptedTermsAdmin(admin.ModelAdmin):
    search_fields = ['User__username']


class FeedbackReportAdmin(admin.ModelAdmin):
    list_filter = ['Status']


admin.site.register(Term)
admin.site.register(UserAcceptedTerms, UserAcceptedTermsAdmin)
admin.site.register(UserMeta, UserMetaAdmin)
admin.site.register(Broadcast)
admin.site.register(FeedbackReport, FeedbackReportAdmin)
admin.site.register(Track)
