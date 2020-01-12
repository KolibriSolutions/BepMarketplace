#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
import os
import django
import argparse
import sys
import json

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='exports distributions in json')
    parser.add_argument('--mode', nargs='?', const=1, type=str, default='debug', help='debug/production')
    parser.add_argument('--timeslot', nargs='?', const=1, type=int, default=-1, help='timeslot')
    parser.add_argument('--list-timeslots', action='store_true')

    MODE, SLOT, DUMP = parser.parse_args().mode, parser.parse_args().timeslot, parser.parse_args().list_timeslots

    if MODE not in ["debug", "production"]:
        sys.exit(1)

    if MODE == 'debug':
        os.environ['DJANGO_SETTINGS_MODULE'] = 'BepMarketplace.settings_development'
    elif MODE == 'production':
        os.environ['DJANGO_SETTINGS_MODULE'] = 'BepMarketplace.settings'

    django.setup()

    from students.models import Distribution
    from timeline.models import TimeSlot

    if DUMP:
        print(json.dumps([t.End.year for t in TimeSlot.objects.all()]))
        sys.exit(0)

    data = {}
    if SLOT != -1:
        timeslot = TimeSlot.objects.get(End__year=SLOT)
        dists = Distribution.objects.filter(Proposal__TimeSlot=timeslot)
    else:
        dists = Distribution.objects.all()



    for dist in dists:
        data[dist.Student.email] = dist.Proposal.Group

    print(json.dumps(data))
