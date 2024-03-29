#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE

# Generated by Django 2.1.4 on 2019-07-01 13:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('presentations', '0003_auto_20190614_1716'),
    ]

    operations = [
        migrations.AlterField(
            model_name='presentationset',
            name='AssessmentRoom',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='assessmentroom', to='presentations.Room'),
        ),
        migrations.AlterField(
            model_name='presentationset',
            name='PresentationOptions',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='presentationsets', to='presentations.PresentationOptions'),
        ),
        migrations.AlterField(
            model_name='presentationset',
            name='PresentationRoom',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='presentationroom', to='presentations.Room'),
        ),
    ]
