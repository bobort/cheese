# Generated by Django 2.1.7 on 2019-04-01 03:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0011_auto_20190320_0221'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zoom_id', models.CharField(max_length=10)),
            ],
        ),
        migrations.AlterModelOptions(
            name='student',
            options={'ordering': ('last_name',), 'verbose_name': 'Student'},
        ),
        migrations.AlterField(
            model_name='appointment',
            name='dt',
            field=models.DateTimeField(verbose_name='Appointment Date and Time'),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='location',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='profile.Product'),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='student',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='groupsession',
            name='appointment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profile.Appointment'),
        ),
    ]
