# Generated by Django 3.2.12 on 2022-03-31 15:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0032_auto_20220328_2338'),
    ]

    operations = [
        migrations.RenameField(
            model_name='parametersetperiod',
            old_name='graph_end_period_number',
            new_name='graph_1_end_period_number',
        ),
        migrations.RenameField(
            model_name='parametersetperiod',
            old_name='graph_start_period_number',
            new_name='graph_1_start_period_number',
        ),
    ]
