#  Bep Marketplace ELE
#  Copyright (c) 2016-2021 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import professionalskills.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('timeline', '0001_initial'),
        ('students', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileExtension',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='FileType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=256)),
                ('Deadline', models.DateField()),
                ('Description', models.CharField(max_length=2056)),
                ('CheckedBySupervisor', models.BooleanField(default=True)),
                ('AllowedExtensions', models.ManyToManyField(to='professionalskills.FileExtension')),
                ('TimeSlot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='filetypes', to='timeline.TimeSlot')),
            ],
        ),
        migrations.CreateModel(
            name='StaffReponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TimestampCreated', models.DateTimeField(auto_now_add=True)),
                ('TimestampLastEdited', models.DateTimeField(auto_now=True)),
                ('Explanation', models.CharField(blank=True, max_length=2048, null=True)),
                ('Status', models.CharField(choices=[('O', 'Insufficient'), ('V', 'Sufficient'), ('G', 'Good')], max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='StudentFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Caption', models.CharField(blank=True, max_length=200, null=True)),
                ('OriginalName', models.CharField(blank=True, max_length=200, null=True)),
                ('File', models.FileField(default=None, upload_to=professionalskills.models.StudentFile.make_upload_path)),
                ('TimeStamp', models.DateTimeField(auto_now=True)),
                ('Created', models.DateTimeField(auto_now_add=True, null=True)),
                ('Distribution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='students.Distribution')),
                ('Type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='professionalskills.FileType')),
            ],
        ),
        migrations.CreateModel(
            name='StudentGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Number', models.IntegerField()),
                ('Start', models.DateTimeField()),
                ('Max', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('Members', models.ManyToManyField(related_name='studentgroups', to=settings.AUTH_USER_MODEL)),
                ('PRV', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='groups', to='professionalskills.FileType')),
            ],
            options={
                'ordering': ['PRV', 'Number'],
            },
        ),
        migrations.AddField(
            model_name='staffreponse',
            name='File',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='professionalskills.StudentFile'),
        ),
        migrations.AddField(
            model_name='staffreponse',
            name='Staff',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fileresponses', to=settings.AUTH_USER_MODEL),
        ),
    ]
