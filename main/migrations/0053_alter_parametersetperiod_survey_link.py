# Generated by Django 3.2.12 on 2022-05-02 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0052_sessionplayerchat_show_time_stamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parametersetperiod',
            name='survey_link',
            field=models.CharField(blank=True, default='', max_length=1000, verbose_name='Survey Link'),
        ),
    ]
