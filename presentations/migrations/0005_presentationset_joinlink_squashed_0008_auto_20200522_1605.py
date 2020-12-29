#  Bep Marketplace ELE
#  Copyright (c) 2016-2021 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE

# Generated by Django 3.0.6 on 2020-05-22 14:06

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('presentations', '0004_auto_20190701_1527'),
    ]

    operations = [
        migrations.AddField(
            model_name='presentationset',
            name='JoinLink',
            field=models.URLField(blank=True, help_text='If the presentation is given in an online platform, a join link for the set can be specified here. The URL has to start with "https://"', max_length=2000, null=True, validators=[django.core.validators.URLValidator(schemes=['https'])]),
        ),
    ]
