# Generated by Django 4.1.4 on 2023-01-03 22:50

import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0069_parametersetpayblock_parametersetpayblockpayment_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='parameterset',
            name='json_for_session',
            field=models.JSONField(blank=True, encoder=django.core.serializers.json.DjangoJSONEncoder, null=True),
        ),
    ]
