# Generated by Django 3.0.8 on 2020-11-09 11:08

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('proposals', '0003_auto_20190701_1527'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='Assistants',
            field=models.ManyToManyField(blank=True, help_text='Add an assistant to the project. If the assistant is not found in the list, ask him/her to login at least once in the system.', related_name='proposals', to=settings.AUTH_USER_MODEL),
        ),
    ]