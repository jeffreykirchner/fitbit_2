# Generated by Django 3.2.12 on 2022-03-31 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0034_auto_20220331_1603'),
    ]

    operations = [
        migrations.AddField(
            model_name='parametersetperiod',
            name='show_graph_2',
            field=models.BooleanField(default=False, verbose_name='Show Graph 2'),
        ),
        migrations.AlterField(
            model_name='parametersetperiod',
            name='show_graph_1',
            field=models.BooleanField(default=False, verbose_name='Show Graph 1'),
        ),
    ]