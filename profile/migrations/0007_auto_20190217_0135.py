# Generated by Django 2.1.4 on 2019-02-17 07:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0006_auto_20190217_0025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderlineitem',
            name='charge',
            field=models.DecimalField(decimal_places=2, max_digits=6, verbose_name='Charge (USD)'),
        ),
        migrations.AlterField(
            model_name='product',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]
