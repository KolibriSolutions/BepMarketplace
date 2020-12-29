#  Bep Marketplace ELE
#  Copyright (c) 2016-2021 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import tracking.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('proposals', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplicationTracking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Timestamp', models.DateTimeField(auto_now_add=True)),
                ('Type', models.CharField(choices=[('a', 'applied'), ('r', 'retracted')], max_length=1)),
                ('Proposal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applicationtrackings', to='proposals.Proposal')),
                ('Student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applicationtrackings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CanvasLogin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Timestamp', models.DateTimeField(auto_now_add=True)),
                ('Subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logins_canvas', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProposalStatusChange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Timestamp', models.DateTimeField(auto_now_add=True)),
                ('StatusFrom', models.IntegerField(choices=[(1, 'Draft, awaiting completion by type 2 (assistant)'), (2, 'Draft, awaiting approval by type 1 (professor)'), (3, 'On hold, awaiting approval track head'), (4, 'Active proposal')], default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(4)])),
                ('StatusTo', models.IntegerField(choices=[(1, 'Draft, awaiting completion by type 2 (assistant)'), (2, 'Draft, awaiting approval by type 1 (professor)'), (3, 'On hold, awaiting approval track head'), (4, 'Active proposal')], default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(4)])),
                ('Message', models.CharField(blank=True, max_length=500, null=True)),
                ('Actor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='StatusChangeTracking', to=settings.AUTH_USER_MODEL)),
                ('Subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='StatusChangeTracking', to='proposals.Proposal')),
            ],
        ),
        migrations.CreateModel(
            name='ProposalTracking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Subject', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='tracking', to='proposals.Proposal')),
                ('UniqueVisitors', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TelemetryKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Created', models.DateTimeField(auto_now_add=True)),
                ('ValidUntil', models.DateField(blank=True, null=True)),
                ('Key', models.CharField(default=tracking.models.generate_key, max_length=64, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserLogin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Timestamp', models.DateTimeField(auto_now_add=True)),
                ('Twofactor', models.BooleanField(default=False)),
                ('Subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logins', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
