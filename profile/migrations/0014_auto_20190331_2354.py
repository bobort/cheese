# Generated by Django 2.1.7 on 2019-04-01 04:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0013_auto_20190331_2308'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupsession',
            name='zoom_id',
            field=models.CharField(help_text='Just enter the numbers, not the hyphens.', max_length=10),
        ),
    ]
