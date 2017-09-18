from django.contrib import admin
from .models import Track, Broadcast, FeedbackReport, UserMeta

admin.site.register(Track)
admin.site.register(Broadcast)
admin.site.register(FeedbackReport)
admin.site.register(UserMeta)