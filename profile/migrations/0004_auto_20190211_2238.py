# Generated by Django 2.1.4 on 2019-02-12 04:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0003_auto_20190106_2114'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('notes', models.TextField()),
                ('exam', models.IntegerField(choices=[(4, 'COMLEX Level 1'), (5, 'COMLEX Level 2'), (6, 'COMLEX Level 3'), (8, 'Medical School Year 1 & 2 Coaching'), (9, 'Medical School Year 3 & 4 Coaching'), (7, 'Specialty Board Certification'), (0, 'USMLE Step 1'), (1, 'USMLE Step 2CK'), (2, 'USMLE Step 2CS'), (3, 'USMLE Step 3'), (10, 'Other'), (11, 'All')], null=True)),
                ('charge', models.DecimalField(decimal_places=2, max_digits=6)),
            ],
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='charge',
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='type',
        ),
        migrations.AlterField(
            model_name='examscore',
            name='exam',
            field=models.IntegerField(choices=[(4, 'COMLEX Level 1'), (5, 'COMLEX Level 2'), (6, 'COMLEX Level 3'), (8, 'Medical School Year 1 & 2 Coaching'), (9, 'Medical School Year 3 & 4 Coaching'), (7, 'Specialty Board Certification'), (0, 'USMLE Step 1'), (1, 'USMLE Step 2CK'), (2, 'USMLE Step 2CS'), (3, 'USMLE Step 3'), (10, 'Other'), (11, 'All')]),
        ),
        migrations.AlterField(
            model_name='student',
            name='degree',
            field=models.IntegerField(choices=[(0, 'MD'), (1, 'DO')], help_text='MD or DO', null=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='exam',
            field=models.IntegerField(choices=[(4, 'COMLEX Level 1'), (5, 'COMLEX Level 2'), (6, 'COMLEX Level 3'), (8, 'Medical School Year 1 & 2 Coaching'), (9, 'Medical School Year 3 & 4 Coaching'), (7, 'Specialty Board Certification'), (0, 'USMLE Step 1'), (1, 'USMLE Step 2CK'), (2, 'USMLE Step 2CS'), (3, 'USMLE Step 3'), (10, 'Other'), (11, 'All')], help_text='Choose the exam you are preparing for.', null=True),
        ),
        migrations.AddField(
            model_name='appointment',
            name='product',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='profile.Product'),
            preserve_default=False,
        ),
    ]
