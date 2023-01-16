# Generated by Django 4.1.4 on 2023-01-12 23:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0085_delete_parametersetperiodpayment'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionperiod',
            name='is_last_period_in_block',
            field=models.BooleanField(default=False, verbose_name='Last Period in block'),
        ),
        migrations.DeleteModel(
            name='ParameterSetZoneMinutes',
        ),
    ]