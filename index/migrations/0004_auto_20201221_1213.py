#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE

# Generated by Django 3.0.8 on 2020-12-21 11:13

from django.db import migrations, models
import timeline.utils


class Migration(migrations.Migration):

    dependencies = [
        ('timeline', '0002_auto_20190302_1431'),
        ('index', '0003_auto_20200517_1518'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermeta',
            name='Cohort',
            field=models.IntegerField(blank=True, help_text='Start year of students study', null=True),
        ),
        migrations.AlterField(
            model_name='usermeta',
            name='EnrolledBEP',
            field=models.BooleanField(default=False, help_text='Whether student user is enrolled in BEP course.'),
        ),
        migrations.AlterField(
            model_name='usermeta',
            name='EnrolledExt',
            field=models.BooleanField(default=False, help_text='Whether student user is enrolled in BEP-extension course.'),
        ),
        migrations.AlterField(
            model_name='usermeta',
            name='Overruled',
            field=models.BooleanField(default=False, help_text='Set to True to not update certain fields during login of user.'),
        ),
        migrations.AlterField(
            model_name='usermeta',
            name='SuppressStatusMails',
            field=models.BooleanField(default=False, help_text='set to True to receive less emails from the system.'),
        ),
        migrations.AlterField(
            model_name='usermeta',
            name='TimeSlot',
            field=models.ManyToManyField(blank=True, default=timeline.utils.get_timeslot_id, help_text='Time slots where the user (student) is active in.', related_name='users', to='timeline.TimeSlot'),
        ),
    ]
