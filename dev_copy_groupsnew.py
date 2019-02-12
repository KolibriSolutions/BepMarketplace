import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'BepMarketplace.settings_development'
django.setup()

from proposals.models import Proposal
from support.models import CapacityGroup

for p in Proposal.objects.all():
    p.Group = CapacityGroup.objects.get(ShortName__iexact=p.Group)
    p.save()
