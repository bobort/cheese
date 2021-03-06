# Generated by Django 3.0.5 on 2020-06-21 02:55

from django.db import migrations, models
import django.db.models.deletion
import drill.models


class Migration(migrations.Migration):

    dependencies = [
        ('drill', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='topic',
            field=models.ForeignKey(default=drill.models.get_last_drill_topic, on_delete=django.db.models.deletion.CASCADE, to='drill.DrillTopic'),
        ),
    ]
