# Generated by Django 2.1.5 on 2019-03-02 15:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('professionalskills', '0002_auto_20190215_1413'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaffResponseFileAspect',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=255)),
                ('Description', models.TextField()),
                ('File', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aspects', to='professionalskills.FileType')),
            ],
        ),
        migrations.CreateModel(
            name='StaffResponseFileAspectResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Grade', models.CharField(blank=True, choices=[('F', 'Fail'), ('S', 'Sufficient'), ('G', 'Good'), ('VG', 'Very Good'), ('E', 'Excellent')], max_length=2, null=True)),
                ('Aspect', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='professionalskills.StaffResponseFileAspect')),
                ('Response', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aspects', to='professionalskills.StaffResponse')),
            ],
        ),
    ]