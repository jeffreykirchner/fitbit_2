# Generated by Django 4.1.4 on 2023-01-06 17:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0079_parameterset_json_for_subject_json'),
    ]

    operations = [
        migrations.RenameField(
            model_name='parameterset',
            old_name='json_for_session',
            new_name='json_for_session_json',
        ),
    ]