# Generated by Django 4.1.4 on 2023-01-06 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0080_rename_json_for_session_parameterset_json_for_session_json'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parametersetpayblock',
            name='pay_block_type',
            field=models.CharField(choices=[('Fixed Pay Only', 'Fixed Pay Only'), ('Block Pay Group', 'Block Pay Group'), ('Block Pay Individual', 'Block Pay Individual'), ('Earn Fitbit', 'Earn Fitbit')], default='Fixed Pay Only', max_length=100),
        ),
    ]