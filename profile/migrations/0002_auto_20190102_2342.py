# Generated by Django 2.1.4 on 2019-01-03 05:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='order_number',
            field=models.CharField(default=0, max_length=7),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='examscore',
            name='exam',
            field=models.IntegerField(choices=[(4, 'COMLEX Level 1'), (5, 'COMLEX Level 2'), (6, 'COMLEX Level 3'), (8, 'Medical School Year 1 & 2 Coaching'), (9, 'Medical School Year 3 & 4 Coaching'), (7, 'Specialty Board Certification'), (0, 'USMLE Step 1'), (1, 'USMLE Step 2CK'), (2, 'USMLE Step 2CS'), (3, 'USMLE Step 3'), (10, 'Other')]),
        ),
        migrations.AlterField(
            model_name='student',
            name='exam',
            field=models.IntegerField(choices=[(4, 'COMLEX Level 1'), (5, 'COMLEX Level 2'), (6, 'COMLEX Level 3'), (8, 'Medical School Year 1 & 2 Coaching'), (9, 'Medical School Year 3 & 4 Coaching'), (7, 'Specialty Board Certification'), (0, 'USMLE Step 1'), (1, 'USMLE Step 2CK'), (2, 'USMLE Step 2CS'), (3, 'USMLE Step 3'), (10, 'Other')], help_text='Choose the exam you are preparing for.', null=True),
        ),
    ]
