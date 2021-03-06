# Generated by Django 3.2.12 on 2022-03-17 18:53

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_auto_20220317_1835'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sessionplayer',
            name='earnings',
        ),
        migrations.AddField(
            model_name='parametersetplayer',
            name='display_color',
            field=models.CharField(default='#000000', max_length=300, verbose_name='Graph Color'),
        ),
        migrations.AddField(
            model_name='session',
            name='cancelation_text',
            field=models.CharField(default='', max_length=10000),
        ),
        migrations.AddField(
            model_name='session',
            name='cancelation_text_subject',
            field=models.CharField(default='', max_length=1000),
        ),
        migrations.AddField(
            model_name='session',
            name='canceled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='session',
            name='end_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='sessionplayer',
            name='disabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='sessionplayer',
            name='group_number',
            field=models.IntegerField(default=1, verbose_name='Group Number'),
        ),
    ]
