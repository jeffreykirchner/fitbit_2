# Generated by Django 3.2.12 on 2022-03-28 23:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0031_auto_20220328_2027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sessionplayerperiod',
            name='earnings_group',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='Individual Earnings'),
        ),
        migrations.AlterField(
            model_name='sessionplayerperiod',
            name='earnings_individual',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='Individual Earnings'),
        ),
    ]