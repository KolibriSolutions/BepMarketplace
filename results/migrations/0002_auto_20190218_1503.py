#  Bep Marketplace ELE
#  Copyright (c) 2016-2021 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='categoryaspectresult',
            options={'ordering': ['CategoryAspect']},
        ),
        migrations.AlterModelOptions(
            name='gradecategoryaspect',
            options={'ordering': ['Category', 'Name']},
        ),
    ]
