# Generated by Django 3.2.12 on 2022-05-07 18:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0057_remove_parameterset_display_block'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionplayerperiod',
            name='fibit_age',
            field=models.IntegerField(default=0),
        ),
    ]
