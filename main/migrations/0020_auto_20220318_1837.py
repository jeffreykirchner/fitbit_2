# Generated by Django 3.2.12 on 2022-03-18 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_auto_20220317_1853'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parameterset',
            name='period_count',
        ),
        migrations.AddField(
            model_name='parameterset',
            name='display_block',
            field=models.IntegerField(default=28, verbose_name='Number of Periods to Display'),
        ),
    ]
