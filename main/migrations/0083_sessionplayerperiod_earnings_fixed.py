# Generated by Django 4.1.4 on 2023-01-09 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0082_sessionplayerperiod_average_pay_block_zone_minutes'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionplayerperiod',
            name='earnings_fixed',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='Fixed Pay Earnings'),
        ),
    ]
