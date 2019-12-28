#  Bep Marketplace ELE
#  Copyright (c) 2016-2019 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('support', '0002_auto_20190212_1629'),
    ]

    operations = [
        migrations.CreateModel(
            name='MailTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('RecipientsStudents', models.CharField(max_length=400)),
                ('RecipientsStaff', models.CharField(max_length=400)),
                ('Subject', models.CharField(max_length=400)),
                ('Message', models.TextField()),
                ('TimeStamp', models.DateTimeField(auto_now=True, null=True)),
                ('Created', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
    ]
