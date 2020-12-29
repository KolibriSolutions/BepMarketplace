#  Bep Marketplace ELE
#  Copyright (c) 2016-2021 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import timeline.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('timeline', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Broadcast',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Message', models.CharField(max_length=512)),
                ('DateBegin', models.DateField(blank=True, null=True)),
                ('DateEnd', models.DateField(blank=True, null=True)),
                ('Private', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='private_broadcasts', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FeedbackReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Url', models.CharField(max_length=255)),
                ('Feedback', models.CharField(max_length=1024)),
                ('Timestamp', models.DateTimeField(auto_now_add=True)),
                ('Status', models.IntegerField(choices=[(1, 'Open'), (2, 'Confirmed'), (3, 'Closed')], validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(3)])),
                ('Reporter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedbackreports', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Term',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Text', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Track',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=255, unique=True)),
                ('ShortName', models.CharField(max_length=10, unique=True)),
                ('Head', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tracks', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserAcceptedTerms',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Stamp', models.DateTimeField(auto_now_add=True)),
                ('User', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='termsaccepted', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserMeta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('SuppressStatusMails', models.BooleanField(default=False)),
                ('Department', models.CharField(blank=True, max_length=512, null=True)),
                ('Study', models.CharField(blank=True, max_length=512, null=True)),
                ('Cohort', models.IntegerField(blank=True, null=True)),
                ('Studentnumber', models.CharField(blank=True, max_length=10, null=True)),
                ('Culture', models.CharField(blank=True, max_length=32, null=True)),
                ('Initials', models.CharField(blank=True, max_length=32, null=True)),
                ('Fullname', models.CharField(blank=True, max_length=32, null=True)),
                ('ECTS', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(300)])),
                ('EnrolledBEP', models.BooleanField(default=False)),
                ('EnrolledExt', models.BooleanField(default=False)),
                ('Overruled', models.BooleanField(default=False)),
                ('TimeSlot', models.ManyToManyField(default=timeline.utils.get_timeslot_id, related_name='users', to='timeline.TimeSlot')),
                ('User', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
