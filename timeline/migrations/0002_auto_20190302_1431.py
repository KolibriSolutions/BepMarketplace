#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('timeline', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='timephase',
            options={'ordering': ['TimeSlot', 'Begin']},
        ),
        migrations.RenameField(
            model_name='timephase',
            old_name='Timeslot',
            new_name='TimeSlot',
        ),
    ]
