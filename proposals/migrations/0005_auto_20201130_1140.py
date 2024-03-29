#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE

# Generated by Django 3.0.8 on 2020-11-30 10:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('timeline', '0002_auto_20190302_1431'),
        ('proposals', '0004_auto_20201109_1208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='TimeSlot',
            field=models.ForeignKey(blank=True, help_text='The year this proposal is used. Set to "Future" to save the proposal for a future time. Only the proposals of the current timeslot can be used in the current timeslot.', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='proposals', to='timeline.TimeSlot'),
        ),
    ]
