# Generated by Django 3.2.12 on 2022-04-04 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0035_auto_20220331_1603'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionplayer',
            name='fitbit_user_id',
            field=models.CharField(default='', max_length=100, verbose_name='FitBit User ID'),
        ),
    ]