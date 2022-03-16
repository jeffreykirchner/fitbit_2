# Generated by Django 4.0.3 on 2022-03-15 21:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_alter_parametersetperiod_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParameterSetPeriodPayments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('group_bonus', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('parameter_set_period', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parameter_set_period_individual_pays_a', to='main.parametersetperiod')),
                ('parameter_set_zone_minutes', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parameter_set_period_individual_pays_b', to='main.parametersetzoneminutes')),
            ],
            options={
                'verbose_name': 'Parameter Set Period Pay',
                'verbose_name_plural': 'Parameter Set Payments',
            },
        ),
        migrations.DeleteModel(
            name='ParameterSetPeriodIndividualPay',
        ),
        migrations.AddConstraint(
            model_name='parametersetperiodpayments',
            constraint=models.UniqueConstraint(fields=('parameter_set_period', 'parameter_set_zone_minutes'), name='unique_parameter_set_payments'),
        ),
    ]
