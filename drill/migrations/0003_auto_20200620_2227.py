# Generated by Django 3.0.5 on 2020-06-21 03:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drill', '0002_auto_20200620_2155'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ('id',)},
        ),
    ]
