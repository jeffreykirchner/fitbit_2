# Generated by Django 4.0.3 on 2022-03-14 20:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_rename_private_chat_parameterset_enable_chat_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParameterSetPeriod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period_number', models.CharField(default=1, max_length=2, verbose_name='ID Label')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('parameter_set', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parameter_set_periods', to='main.parameterset')),
            ],
            options={
                'verbose_name': 'Parameter Set Player',
                'verbose_name_plural': 'Parameter Set Players',
                'ordering': ['period_number'],
            },
        ),
    ]
