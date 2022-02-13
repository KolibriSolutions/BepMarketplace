#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('students', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('index', '0001_initial'),
        ('timeline', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PresentationOptions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('PresentationDuration', models.IntegerField(default=15, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)])),
                ('AssessmentDuration', models.IntegerField(default=15, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)])),
                ('PresentationsBeforeAssessment', models.IntegerField(default=3, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('Public', models.BooleanField(default=False)),
                ('TimeSlot', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='presentationoptions', to='timeline.TimeSlot')),
            ],
        ),
        migrations.CreateModel(
            name='PresentationSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('DateTime', models.DateTimeField()),
            ],
            options={
                'ordering': ['PresentationRoom'],
            },
        ),
        migrations.CreateModel(
            name='PresentationTimeSlot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('DateTime', models.DateTimeField()),
                ('CustomType', models.IntegerField(choices=[(1, 'Assessment'), (2, 'Break')], default=0, null=True)),
                ('CustomDuration', models.IntegerField(blank=True, default=None, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)])),
                ('Distribution', models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='presentationtimeslot', to='students.Distribution')),
                ('Presentations', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='timeslots', to='presentations.PresentationSet')),
            ],
            options={
                'ordering': ['DateTime'],
            },
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='presentationset',
            name='AssessmentRoom',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assessmentroom', to='presentations.Room'),
        ),
        migrations.AddField(
            model_name='presentationset',
            name='Assessors',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='presentationset',
            name='PresentationOptions',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='presentationsets', to='presentations.PresentationOptions'),
        ),
        migrations.AddField(
            model_name='presentationset',
            name='PresentationRoom',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='presentationroom', to='presentations.Room'),
        ),
        migrations.AddField(
            model_name='presentationset',
            name='Track',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='index.Track'),
        ),
    ]
