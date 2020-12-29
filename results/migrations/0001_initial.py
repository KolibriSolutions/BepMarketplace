#  Bep Marketplace ELE
#  Copyright (c) 2016-2021 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import timeline.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('timeline', '0001_initial'),
        ('students', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryAspectResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Grade', models.CharField(blank=True, choices=[('F', 'Fail (< 6)'), ('S', 'Sufficient (6-7)'), ('G', 'Good (7-8)'), ('VG', 'Very Good (8-9)'), ('E', 'Excellent (9-10)')], max_length=2, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CategoryResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Grade', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)])),
                ('Comments', models.TextField(blank=True, null=True)),
                ('Final', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['Category'],
            },
        ),
        migrations.CreateModel(
            name='GradeCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Weight', models.FloatField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('Name', models.CharField(max_length=255)),
                ('TimeSlot', models.ForeignKey(default=timeline.utils.get_timeslot_id, on_delete=django.db.models.deletion.PROTECT, related_name='gradecategories', to='timeline.TimeSlot')),
            ],
            options={
                'ordering': ['-Weight', 'Name'],
            },
        ),
        migrations.CreateModel(
            name='GradeCategoryAspect',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=255)),
                ('Description', models.TextField()),
                ('Category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aspects', to='results.GradeCategory')),
            ],
        ),
        migrations.CreateModel(
            name='ResultOptions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Visible', models.BooleanField(default=False)),
                ('TimeSlot', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='resultoptions', to='timeline.TimeSlot')),
            ],
        ),
        migrations.AddField(
            model_name='categoryresult',
            name='Category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='results.GradeCategory'),
        ),
        migrations.AddField(
            model_name='categoryresult',
            name='Distribution',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='students.Distribution'),
        ),
        migrations.AddField(
            model_name='categoryaspectresult',
            name='CategoryAspect',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='results.GradeCategoryAspect'),
        ),
        migrations.AddField(
            model_name='categoryaspectresult',
            name='CategoryResult',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aspectresults', to='results.CategoryResult'),
        ),
    ]
