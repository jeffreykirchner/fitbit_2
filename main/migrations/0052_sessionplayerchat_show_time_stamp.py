# Generated by Django 3.2.12 on 2022-04-28 23:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0051_auto_20220428_2118'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionplayerchat',
            name='show_time_stamp',
            field=models.BooleanField(default=False),
        ),
    ]
