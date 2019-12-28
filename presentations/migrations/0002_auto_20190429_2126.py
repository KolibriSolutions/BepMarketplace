#  Bep Marketplace ELE
#  Copyright (c) 2016-2019 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('presentations', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='presentationset',
            options={'ordering': ['DateTime']},
        ),
    ]
