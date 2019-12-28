#  Bep Marketplace ELE
#  Copyright (c) 2016-2019 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0003_auto_20190220_1635'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categoryaspectresult',
            name='Grade',
            field=models.CharField(blank=True, choices=[('F', 'Fail'), ('S', 'Sufficient'), ('G', 'Good'), ('VG', 'Very Good'), ('E', 'Excellent')], max_length=2, null=True),
        ),
    ]
