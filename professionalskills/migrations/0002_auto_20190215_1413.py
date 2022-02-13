#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('professionalskills', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='StaffReponse',
            new_name='StaffResponse',
        ),
    ]
