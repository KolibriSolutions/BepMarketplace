#  Bep Marketplace ELE
#  Copyright (c) 2016-2019 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TimePhase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Description', models.IntegerField(choices=[(1, 'Generating project proposals'), (2, 'Projects quality check'), (3, 'Students choosing projects'), (4, 'Distribution of projects'), (5, 'Gather and process objections'), (6, 'Execution of the projects'), (7, 'Presentation of results')])),
                ('Begin', models.DateField()),
                ('End', models.DateField()),
                ('CountdownEnd', models.DateField(blank=True, help_text='Fake end date, to set the homepage clock to an earlier date. A trick to motivate people.', null=True)),
            ],
            options={
                'ordering': ['Timeslot', 'Begin'],
            },
        ),
        migrations.CreateModel(
            name='TimeSlot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=250)),
                ('Begin', models.DateField()),
                ('End', models.DateField()),
            ],
            options={
                'ordering': ['Begin'],
            },
        ),
        migrations.AddField(
            model_name='timephase',
            name='Timeslot',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='timephases', to='timeline.TimeSlot'),
        ),
    ]
