# Generated by Django 3.2.12 on 2022-05-04 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0055_auto_20220503_2351'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sessionplayer',
            name='fitbit_user_id',
            field=models.CharField(blank=True, default='', max_length=100, null=True, verbose_name='FitBit User ID'),
        ),
        migrations.AlterField(
            model_name='sessionplayer',
            name='name',
            field=models.CharField(blank=True, default='', max_length=100, null=True, verbose_name='Full Name'),
        ),
        migrations.AlterField(
            model_name='sessionplayer',
            name='student_id',
            field=models.CharField(blank=True, default='', max_length=100, null=True, verbose_name='Student ID'),
        ),
    ]
