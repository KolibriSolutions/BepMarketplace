#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE

# Generated by Django 2.1.4 on 2019-07-01 13:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0005_auto_20190429_2126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categoryaspectresult',
            name='CategoryAspect',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='results', to='results.GradeCategoryAspect'),
        ),
        migrations.AlterField(
            model_name='categoryresult',
            name='Category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='results', to='results.GradeCategory'),
        ),
        migrations.AlterField(
            model_name='resultoptions',
            name='TimeSlot',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='resultoptions', to='timeline.TimeSlot'),
        ),
    ]
