# Generated by Django 3.2.12 on 2022-04-05 22:08

import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0036_sessionplayer_fitbit_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sessionplayerperiod',
            name='fitbit_heart_time_series',
            field=models.JSONField(decoder=django.core.serializers.json.DjangoJSONEncoder, encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
    ]
