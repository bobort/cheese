# Generated by Django 2.1.7 on 2019-04-01 04:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0011_event_calendar_not_null'),
        ('profile', '0012_auto_20190331_2205'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='groupsession',
            name='appointment',
        ),
        migrations.AddField(
            model_name='groupsession',
            name='occurrence',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='schedule.Occurrence'),
            preserve_default=False,
        ),
    ]