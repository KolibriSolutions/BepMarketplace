import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'BepMarketplace.settings_development'
django.setup()

from django.contrib.auth.models import User
from index.models import UserMeta

for user in User.objects.all():
    try:
        meta = user.usermeta
    except UserMeta.DoesNotExist:
        meta = UserMeta(User=user)
        meta.save()
