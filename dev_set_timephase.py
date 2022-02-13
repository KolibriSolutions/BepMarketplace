#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
import os

import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'BepMarketplace.settings_development'
django.setup()

import argparse
from timeline.models import TimePhase
from datetime import datetime, timedelta
from timeline.utils import get_timeslot
from django.core.cache import cache

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Nr: \
                                                1:Generating project proposals\
                                                2:Projects quality check; \
                                                3:Students choosing projects; \
                                                4:Distribution of projects; \
                                                5:Gather and process objections; \
                                                6:Execution of the projects; \
                                                7:Presentation of results")
    parser.add_argument('p', nargs='?', const=1, type=str, default='0', help='timephase number')
    n = int(parser.parse_args().p)
    assert n >= 0, 'too low number'
    assert n <= 7, 'too high number'
    TimePhase.objects.all().delete()
    if n > 0:
        t = TimePhase(Begin=datetime.now() - timedelta(days=2),
                      End=datetime.now() + timedelta(days=40),
                      Description=n,
                      TimeSlot=get_timeslot())
        t.save()
        print('Set phase {}'.format(t))
    else:
        print('Cleared all phases')
    cache.clear()
