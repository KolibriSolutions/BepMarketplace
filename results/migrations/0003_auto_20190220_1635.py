#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('professionalskills', '0002_auto_20190215_1413'),
        ('results', '0002_auto_20190218_1503'),
    ]

    operations = [
        migrations.AddField(
            model_name='categoryresult',
            name='Files',
            field=models.ManyToManyField(blank=True, related_name='results', to='professionalskills.StudentFile'),
        ),
        migrations.AddField(
            model_name='gradecategory',
            name='File',
            field=models.ForeignKey(blank=True, help_text='If this category is to grade a file or professional skill, select the file type here.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='results', to='professionalskills.FileType'),
        ),
    ]
