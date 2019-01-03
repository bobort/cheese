# Generated by Django 2.1.4 on 2019-01-01 11:29

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import profile.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=150)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_superuser', models.BooleanField(default=False)),
                ('date_joined', models.DateField()),
                ('last_login', models.DateTimeField()),
                ('graduation_year', models.IntegerField(help_text="Enter all 4 digits. If you haven't graduated yet, enter the year you expect to graduate.", null=True, validators=[django.core.validators.MinValueValidator(1900), django.core.validators.MaxValueValidator(2050)])),
                ('degree', models.IntegerField(choices=[(0, 'M.D.'), (1, 'D.O.')], help_text='M.D. or D.O.', null=True)),
                ('exam', models.IntegerField(choices=[(0, 'USMLE Step 1'), (1, 'USMLE Step 2CK'), (2, 'USMLE Step 2CS'), (3, 'USMLE Step 3'), (4, 'USMLE Specialty Board Certification'), (5, 'Other')], help_text='Choose the exam you are preparing for.', null=True)),
                ('test_date', models.DateField(blank=True, help_text='Enter the date that you need to complete the test by or the date you are scheduled to take it.', null=True)),
                ('phone_number', models.CharField(max_length=31, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Student',
            },
            managers=[
                ('objects', profile.managers.StudentManager()),
            ],
        ),
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dt', models.DateTimeField()),
                ('duration', models.DurationField()),
                ('charge', models.DecimalField(decimal_places=2, max_digits=6)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('type', models.IntegerField(choices=[(0, 'In Person'), (1, 'Remote Video Conference')])),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ExamScore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exam', models.IntegerField(choices=[(0, 'USMLE Step 1'), (1, 'USMLE Step 2CK'), (2, 'USMLE Step 2CS'), (3, 'USMLE Step 3'), (4, 'USMLE Specialty Board Certification'), (5, 'Other')])),
                ('score', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(300)])),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_paid', models.DateTimeField(default=django.utils.timezone.now)),
                ('total', models.DecimalField(decimal_places=2, max_digits=6)),
                ('in_person_appt_qty', models.PositiveSmallIntegerField(default=0, verbose_name='Appointments In Person')),
                ('remote_appt_qty', models.PositiveSmallIntegerField(default=0, verbose_name='Appointments Remotely')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]