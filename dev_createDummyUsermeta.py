import argparse
import django
import sys
import os

parser = argparse.ArgumentParser(description="Populate the database with initial values for usermeta")
parser.add_argument('--mode', nargs='?', const=1, type=str, default='debug', help='debug/production')
MODE = parser.parse_args().mode

if MODE not in ["debug", "production"]:
    sys.exit(1)

if MODE == 'debug':
    os.environ['DJANGO_SETTINGS_MODULE'] = 'BepMarketplace.settings_development'
elif MODE == 'production':
    os.environ['DJANGO_SETTINGS_MODULE'] = 'BepMarketplace.settings'

django.setup()

from index.models import UserMeta
from django.contrib.auth.models import User
from random import choice
from django.conf import settings
from proposals.models import Proposal
from students.models import Application

cohorts = [
    '2010',
    '2011',
    '2012',
    '2013',
    '2014',
    '2015'
]

ects = [
    10,
    20,
    30,
    40,
    50,
    60,
    70,
    80,
    90,
    100,
    110,
    120,
    130,
    140,
    150,
    160,
    170,
    180,
    190,
    200
]

study = [
    'Automotive',
    'Elektrotechniek',
    'Elektrotechniek',
    'Elektrotechniek',
]

NUMSTDS = 50

print("generating usermeta")
for n in range(0, NUMSTDS):
    std = User.objects.get(username="std{}".format(n))
    um, created = UserMeta.objects.get_or_create(User=std)
    um.ECTS = choice(ects)
    um.Cohort = choice(cohorts)
    um.Study = choice(study)
    um.Fullname = "std {}".format(n)
    um.EnrolledBEP = True
    um.save()
    print("generated for {}".format(std))

print("generating applications")
projects = Proposal.objects.filter(Status=4)
Application.objects.all().delete()
for n in range(0, NUMSTDS):
    std = User.objects.get(username="std{}".format(n))
    projs = []
    for i in range(0, settings.MAX_NUM_APPLICATIONS):
        app = Application()
        while True:
            p = choice(projects)
            if p not in projs:
                projs.append(p)
                break

        app.Proposal = choice(projects)
        app.Student = std
        app.Priority = i + 1
        app.save()
    print("generated for {}".format(std))