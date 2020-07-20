#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracking', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='telemetrykey',
            old_name='Key',
            new_name='key',
        ),
    ]
