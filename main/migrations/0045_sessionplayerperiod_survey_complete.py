# Generated by Django 3.2.12 on 2022-04-21 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0044_parameters_software_version'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionplayerperiod',
            name='survey_complete',
            field=models.BooleanField(default=True, verbose_name='Survey Complete'),
        ),
    ]
