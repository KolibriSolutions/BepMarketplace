# Generated by Django 3.2.11 on 2022-01-25 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('osirisdata', '0003_osirisdatafile'),
    ]

    operations = [
        migrations.AddField(
            model_name='osirisdatafile',
            name='Created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='osirisdatafile',
            name='TimeStamp',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]