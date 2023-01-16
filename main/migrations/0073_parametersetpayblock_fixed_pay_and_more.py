# Generated by Django 4.1.4 on 2023-01-05 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0072_parametersetpayblockpayment_label'),
    ]

    operations = [
        migrations.AddField(
            model_name='parametersetpayblock',
            name='fixed_pay',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='Individual Payment'),
        ),
        migrations.AddField(
            model_name='parametersetpayblock',
            name='no_pay_percent',
            field=models.IntegerField(default=0, verbose_name='No Pay Fitbit Percent'),
        ),
    ]
