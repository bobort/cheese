# Generated by Django 2.2 on 2019-04-04 02:49

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0011_event_calendar_not_null'),
        ('profile', '0015_auto_20190401_0010'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appointment',
            name='date_created',
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='dt',
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='duration',
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='location',
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='product',
        ),
        migrations.AddField(
            model_name='appointment',
            name='occurrence',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to='schedule.Occurrence'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='examscore',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='examscore',
            name='score',
            field=models.IntegerField(choices=[(1, 'Pass'), (0, 'Fail')]),
        ),
    ]
