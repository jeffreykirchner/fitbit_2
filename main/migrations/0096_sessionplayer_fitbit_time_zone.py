# Generated by Django 4.1.7 on 2023-03-24 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0095_parameterset_reconnection_limit'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionplayer',
            name='fitbit_time_zone',
            field=models.CharField(default='America/Los_Angeles', max_length=100, verbose_name='FitBit Timezone'),
        ),
    ]