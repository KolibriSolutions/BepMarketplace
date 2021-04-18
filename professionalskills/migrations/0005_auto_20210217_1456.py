# Generated by Django 3.1.5 on 2021-02-17 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('professionalskills', '0004_auto_20190701_1527'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staffresponse',
            name='Status',
            field=models.CharField(choices=[('ON', 'Insufficient'), ('VO', 'Sufficient'), ('GO', 'Good')], max_length=2),
        ),
    ]
