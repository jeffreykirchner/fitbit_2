# Generated by Django 4.1.4 on 2023-01-05 00:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0071_alter_parametersetpayblock_pay_block_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='parametersetpayblockpayment',
            name='label',
            field=models.CharField(default='min to min', max_length=20, verbose_name='Label Shown'),
        ),
    ]