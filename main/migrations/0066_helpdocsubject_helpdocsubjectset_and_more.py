# Generated by Django 4.1.4 on 2022-12-12 19:25

from django.db import migrations, models
import django.db.models.deletion
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0065_remove_sessionplayerperiod_fitbit_sleep_time_series_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='HelpDocSubject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=300, verbose_name='Title')),
                ('text', tinymce.models.HTMLField(default='', max_length=100000, verbose_name='Help Doc Text')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Help Doc Subject',
                'verbose_name_plural': 'Help Docs Subject',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='HelpDocSubjectSet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(default='Name Here', max_length=100, verbose_name='Label')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Help Doc Subject Set',
                'verbose_name_plural': 'Help Doc Subject Sets',
                'ordering': ['label'],
            },
        ),
        migrations.AddConstraint(
            model_name='helpdocsubjectset',
            constraint=models.UniqueConstraint(fields=('label',), name='unique_help_doc_subject_set'),
        ),
        migrations.AddField(
            model_name='helpdocsubject',
            name='help_doc_subject_set',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='help_doc_subject', to='main.helpdocsubjectset'),
        ),
        migrations.AddConstraint(
            model_name='helpdocsubject',
            constraint=models.UniqueConstraint(fields=('title', 'help_doc_subject_set'), name='unique_help_doc_subject'),
        ),
    ]