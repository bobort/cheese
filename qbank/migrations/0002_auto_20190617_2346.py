# Generated by Django 2.2 on 2019-06-18 04:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('qbank', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='question',
            old_name='correct_answer_description',
            new_name='explanation_summary',
        ),
        migrations.RenameField(
            model_name='question',
            old_name='description',
            new_name='vignette',
        ),
    ]
