#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('proposals', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('timeline', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Priority', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('Timestamp', models.DateTimeField(auto_now_add=True)),
                ('Proposal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='proposals.Proposal')),
                ('Student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['Priority'],
            },
        ),
        migrations.CreateModel(
            name='Distribution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Application', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='distributions', to='students.Application')),
                ('Proposal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='distributions', to='proposals.Proposal')),
                ('Student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='distributions', to=settings.AUTH_USER_MODEL)),
                ('Timeslot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='distributions', to='timeline.TimeSlot')),
            ],
        ),
    ]
