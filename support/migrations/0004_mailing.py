#  Bep Marketplace ELE
#  Copyright (c) 2016-2021 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('support', '0003_mailtemplate'),
    ]

    operations = [
        migrations.CreateModel(
            name='Mailing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Subject', models.CharField(max_length=400)),
                ('Message', models.TextField()),
                ('Sent', models.BooleanField(default=False)),
                ('TimeStamp', models.DateTimeField(auto_now=True, null=True)),
                ('Created', models.DateTimeField(auto_now_add=True, null=True)),
                ('RecipientsStaff', models.ManyToManyField(blank=True, default=None, related_name='received_mailings_staff', to=settings.AUTH_USER_MODEL)),
                ('RecipientsStudents', models.ManyToManyField(blank=True, default=None, related_name='received_mailings_students', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
