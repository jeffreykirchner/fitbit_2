# Generated by Django 3.2.12 on 2022-05-07 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0058_sessionplayerperiod_fibit_age'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionplayerperiod',
            name='fitbit_resting_heart_rate',
            field=models.IntegerField(default=0),
        ),
    ]
