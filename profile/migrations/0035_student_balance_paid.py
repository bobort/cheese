# Generated by Django 4.1.4 on 2023-04-11 02:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0034_rename_productusers_productuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='balance_paid',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
