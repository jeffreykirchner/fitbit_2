# Generated by Django 4.0.3 on 2022-03-11 17:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_alter_parametersetplayer_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='parametersetplayer',
            options={'ordering': ['id_label'], 'verbose_name': 'Parameter Set Player', 'verbose_name_plural': 'Parameter Set Players'},
        ),
    ]
