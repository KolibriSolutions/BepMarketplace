#  Bep Marketplace ELE
#  Copyright (c) 2016-2019 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
"""
Import type1 users from csv file. Used to initialy create users for professors to give them type1staff status.

"""

import argparse
import csv
import os.path
import sys

import django

if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Load type1 from csv")
    parser.add_argument('--mode', nargs='?', const=1, type=str, default='debug', help='debug/production')
    parser.add_argument('--file', nargs='?', const=1, type=str, default='', help='filename')

    parser.set_defaults(createDummyData=False)
    filename = parser.parse_args().file
    MODE = parser.parse_args().mode

    if MODE not in ["debug", "production"]:
        sys.exit(1)
    if MODE == 'debug':
        os.environ['DJANGO_SETTINGS_MODULE'] = 'BepMarketplace.settings_development'
    elif MODE == 'production':
        os.environ['DJANGO_SETTINGS_MODULE'] = 'BepMarketplace.settings'

    django.setup()

    from django.contrib.auth.models import Group, User

    newusers = []
    if os.path.isfile(filename):
        print('start')
        with open(filename,newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=';')
            for row in spamreader:
                username = (row[2].split("@")[0]).replace('.', '').lower()
                newusers.append([username.strip(),row[2].lower().strip(),row[0].strip(),row[1].strip()]) #user,mail,firstname,lastname
    else:
        print("file does not exist")

    for newuser in newusers:
        print(newuser)
        username,email,firstname,lastname=newuser
        g, created = User.objects.get_or_create(username=username)
        if created:
            g.first_name = firstname
            g.last_name = lastname
            g.email = email
            g.is_staff = False
            g.groups.add(Group.objects.get(name="type1staff"))
            g.save()
        else:
            print("user exists!")
