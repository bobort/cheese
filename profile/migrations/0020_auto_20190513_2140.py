# Generated by Django 2.2 on 2019-05-14 02:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0019_auto_20190512_2147'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='in_person_appt_qty',
            field=models.SmallIntegerField(blank=True, default=0, null=True, verbose_name='In Person Appointments'),
        ),
        migrations.AlterField(
            model_name='order',
            name='remote_appt_qty',
            field=models.SmallIntegerField(blank=True, default=0, null=True, verbose_name='Online Appointments'),
        ),
    ]