#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import support.models
import timeline.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('timeline', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CapacityGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ShortName', models.CharField(max_length=3)),
                ('FullName', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='CapacityGroupAdministration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Group', models.CharField(choices=[('EES', 'Electrical Energy Systems'), ('ECO', 'Electro-Optical Communications'), ('EPE', 'Electromechanics and Power Electronics'), ('ES', 'Electronic Systems'), ('MsM', 'Mixed-signal Microelectronics'), ('CS', 'Control Systems'), ('SPS', 'Signal Processing Systems'), ('PHI', 'Photonic Integration'), ('EM', 'Electromagnetics')], max_length=3)),
                ('Members', models.ManyToManyField(blank=True, related_name='groupadministrations', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GroupAdministratorThrough',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Super', models.BooleanField(blank=True, default=False)),
                ('Group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='support.CapacityGroup')),
                ('User', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='administratoredgroups', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PublicFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Caption', models.CharField(blank=True, max_length=200, null=True)),
                ('OriginalName', models.CharField(blank=True, max_length=200, null=True)),
                ('File', models.FileField(default=None, upload_to=support.models.PublicFile.make_upload_path)),
                ('TimeStamp', models.DateTimeField(auto_now=True, null=True)),
                ('Created', models.DateTimeField(auto_now_add=True, null=True)),
                ('TimeSlot', models.ForeignKey(default=timeline.utils.get_timeslot_id, on_delete=django.db.models.deletion.CASCADE, related_name='public_files', to='timeline.TimeSlot')),
                ('User', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='capacitygroup',
            name='Administrators',
            field=models.ManyToManyField(related_name='administratorgroups', through='support.GroupAdministratorThrough', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='capacitygroup',
            name='Head',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='capacity_group_head', to=settings.AUTH_USER_MODEL),
        ),
    ]
