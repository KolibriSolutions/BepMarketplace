#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE

# Generated by Django 3.0.5 on 2020-05-17 13:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0002_auto_20190504_1211'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='track',
            options={'ordering': ['Name']},
        ),
    ]