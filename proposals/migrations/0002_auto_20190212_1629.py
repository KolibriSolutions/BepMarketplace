#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='Group',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='support.CapacityGroup'),
            preserve_default=False,
        ),
    ]
