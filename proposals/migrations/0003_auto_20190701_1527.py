#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE

# Generated by Django 2.1.4 on 2019-07-01 13:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0002_auto_20190212_1629'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='Group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='support.CapacityGroup'),
        ),
    ]
