from django.contrib import admin

from .models import Track, Broadcast, FeedbackReport, UserMeta, Term, UserAcceptedTerms


class UserMetaAdmin(admin.ModelAdmin):
    search_fields = ['User__username']
    list_filter = ('EnrolledBEP', 'EnrolledExt', 'Cohort')


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
