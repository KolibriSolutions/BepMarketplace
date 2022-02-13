#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
"""
Give students a timeslot. Used for init populations.
"""
import django
import argparse
import sys
import os

parser = argparse.ArgumentParser(description="sets current timeslot on all students")
parser.add_argument('--mode', nargs='?', const=1, type=str, default='debug', help='debug/production')

MODE = parser.parse_args().mode

if MODE not in ["debug", "production"]:
    sys.exit(1)
if MODE == 'debug':
    os.environ['DJANGO_SETTINGS_MODULE'] = 'BepMarketplace.settings_development'
elif MODE == 'production':
    os.environ['DJANGO_SETTINGS_MODULE'] = 'BepMarketplace.settings'

django.setup()

from timeline.utils import get_timeslot
from django.contrib.auth.models import User
from django.db.models import Q

def get_all_students():
    """
    Return all active students in marketplace, used for instance for mailing.

    :return: user objects
    """
    return User.objects.filter(Q(groups=None)).distinct()



ts = get_timeslot()

for std in get_all_students():
    print(std)
    std.usermeta.TimeSlot.add(ts)
    std.usermeta.EnrolledBEP =True
    std.usermeta.save()
    std.save()
