#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import proposals.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('support', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('index', '0001_initial'),
        ('timeline', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Proposal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Title', models.CharField(max_length=100)),
                ('NumStudentsMin', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('NumStudentsMax', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('GeneralDescription', models.TextField()),
                ('StudentsTaskDescription', models.TextField()),
                ('ExtensionDescription', models.TextField(blank=True, null=True)),
                ('Status', models.IntegerField(choices=[(1, 'Draft, awaiting completion by type 2 (assistant)'), (2, 'Draft, awaiting approval by type 1 (professor)'), (3, 'On hold, awaiting approval track head'), (4, 'Active proposal')], default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(4)])),
                ('TimeStamp', models.DateTimeField(auto_now=True, null=True)),
                ('Created', models.DateTimeField(auto_now_add=True, null=True)),
                ('Assistants', models.ManyToManyField(blank=True, related_name='proposals', to=settings.AUTH_USER_MODEL)),
                ('Group', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='support.CapacityGroup')),
                ('Private', models.ManyToManyField(blank=True, related_name='personal_proposal', to=settings.AUTH_USER_MODEL)),
                ('ResponsibleStaff', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='proposalsresponsible', to=settings.AUTH_USER_MODEL)),
                ('TimeSlot', models.ForeignKey(blank=True, help_text='The year this proposal is used. Set to "--" to save the proposal for a future time. Only the proposals of the current timeslot can be used in the current timeslot.', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='proposals', to='timeline.TimeSlot')),
                ('Track', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Track')),
            ],
        ),
        migrations.CreateModel(
            name='ProposalAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Caption', models.CharField(blank=True, max_length=200, null=True)),
                ('OriginalName', models.CharField(blank=True, max_length=200, null=True)),
                ('File', models.FileField(default=None, upload_to=proposals.models.ProposalFile.make_upload_path)),
                ('Proposal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='proposals.Proposal')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProposalImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Caption', models.CharField(blank=True, max_length=200, null=True)),
                ('OriginalName', models.CharField(blank=True, max_length=200, null=True)),
                ('File', models.ImageField(default=None, upload_to=proposals.models.ProposalFile.make_upload_path)),
                ('Proposal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='proposals.Proposal')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='favorite',
            name='Project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to='proposals.Proposal'),
        ),
        migrations.AddField(
            model_name='favorite',
            name='User',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to=settings.AUTH_USER_MODEL),
        ),
    ]
