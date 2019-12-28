#  Bep Marketplace ELE
#  Copyright (c) 2016-2019 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0004_auto_20190222_2221'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='categoryresult',
            name='Files',
        ),
        migrations.RemoveField(
            model_name='gradecategory',
            name='File',
        ),
    ]
