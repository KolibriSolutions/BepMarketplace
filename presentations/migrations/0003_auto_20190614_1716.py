#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('presentations', '0002_auto_20190429_2126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='presentationtimeslot',
            name='CustomType',
            field=models.IntegerField(choices=[(1, 'Assessment'), (2, 'Break'), (3, 'Cancelled')], default=0, null=True),
        ),
    ]
