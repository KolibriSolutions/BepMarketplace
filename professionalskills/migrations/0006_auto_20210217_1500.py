#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE

# Generated by Django 3.1.5 on 2021-02-17 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('professionalskills', '0005_auto_20210217_1456'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staffresponse',
            name='Status',
            field=models.CharField(choices=[('O', 'Insufficient'), ('V', 'Sufficient'), ('G', 'Good')], max_length=1),
        ),
    ]
