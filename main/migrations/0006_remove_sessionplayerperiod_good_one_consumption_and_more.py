# Generated by Django 4.0.3 on 2022-03-14 19:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_alter_parametersetplayer_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sessionplayerperiod',
            name='good_one_consumption',
        ),
        migrations.RemoveField(
            model_name='sessionplayerperiod',
            name='good_one_production',
        ),
        migrations.RemoveField(
            model_name='sessionplayerperiod',
            name='good_one_production_rate',
        ),
        migrations.RemoveField(
            model_name='sessionplayerperiod',
            name='good_three_consumption',
        ),
        migrations.RemoveField(
            model_name='sessionplayerperiod',
            name='good_two_consumption',
        ),
        migrations.RemoveField(
            model_name='sessionplayerperiod',
            name='good_two_production',
        ),
        migrations.RemoveField(
            model_name='sessionplayerperiod',
            name='good_two_production_rate',
        ),
    ]
