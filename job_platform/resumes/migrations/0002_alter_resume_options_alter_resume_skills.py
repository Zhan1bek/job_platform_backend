# Generated by Django 5.1.6 on 2025-05-09 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resumes', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='resume',
            options={},
        ),
        migrations.AlterField(
            model_name='resume',
            name='skills',
            field=models.TextField(blank=True),
        ),
    ]
