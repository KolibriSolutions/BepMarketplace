# Generated by Django 2.1.4 on 2019-02-12 15:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='Group',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='support.CapacityGroup'),
            preserve_default=False,
        ),
    ]