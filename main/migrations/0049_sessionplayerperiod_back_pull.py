# Generated by Django 3.2.12 on 2022-04-27 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0048_auto_20220424_0514'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionplayerperiod',
            name='back_pull',
            field=models.BooleanField(default=False, verbose_name='Back Pull'),
        ),
    ]
