#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE

# Generated by Django 3.0.6 on 2020-06-09 09:58

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('presentations', '0008_auto_20200609_1153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='presentationset',
            name='Assessors',
            field=models.ManyToManyField(blank=True, help_text='Staff member to help or replace the project supervisor in assessing the presentation', related_name='assessors', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='presentationset',
            name='PresentationAssessors',
            field=models.ManyToManyField(blank=True, help_text='ESA/STU person to assess the presentation skills.', related_name='presentation_assessors', to=settings.AUTH_USER_MODEL),
        ),
    ]
