# Generated by Django 4.1.4 on 2023-01-06 17:37

import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0076_remove_parametersetperiod_pay_block'),
    ]

    operations = [
        migrations.AddField(
            model_name='parameterset',
            name='json_for_subject2',
            field=models.JSONField(blank=True, encoder=django.core.serializers.json.DjangoJSONEncoder, null=True),
        ),
    ]
