# Generated by Django 4.1.4 on 2023-01-05 23:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0075_parametersetperiod_parameter_set_pay_block'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parametersetperiod',
            name='pay_block',
        ),
    ]
