from django.contrib import admin
from .models import Track, Broadcast, FeedbackReport, UserMeta, Term, UserAcceptedTerms

admin.site.register(Track)
admin.site.register(Broadcast)
admin.site.register(FeedbackReport)
admin.site.register(UserMeta)
admin.site.register(Term)
admin.site.register(UserAcceptedTerms)