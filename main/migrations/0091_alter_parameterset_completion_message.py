# Generated by Django 4.1.4 on 2023-01-20 22:38

from django.db import migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0090_parameterset_completion_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parameterset',
            name='completion_message',
            field=tinymce.models.HTMLField(blank=True, default='The study is complete, thank you for your participation.', verbose_name='End of study message'),
        ),
    ]
