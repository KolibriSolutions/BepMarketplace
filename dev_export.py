#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
"""
Export groups and tracks.
"""
import os
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'BepMarketplace.settings_development'
django.setup()

from django.core import serializers
from django.contrib.auth.models import Group
from index.models import Track

if __name__=="__main__":
    groups = list(Group.objects.all())
    tracks = list(Track.objects.all())

    with open("groups.json", "w") as stream:
        stream.write(serializers.serialize("json", groups))

    with open("tracks.json", "w") as stream:
        stream.write(serializers.serialize("json", tracks))
