from django.contrib.auth.models import UserManager
from django.db import models
from django.db.models.functions import Now
from django.utils import timezone


class StudentManager(UserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a Student with the given email and password.
        """
        if not email:
            raise ValueError('Students must have an email address.')

        extra_fields['date_joined'] = timezone.now()
        extra_fields['last_login'] = extra_fields['date_joined']
        student = self.model(email=self.normalize_email(email), **extra_fields)
        student.set_password(password)
        student.save(using=self._db)
        return student

    def create_superuser(self, email, password, **extra_fields):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        student = self.create_user(email, password, **extra_fields)
        student.is_superuser = True
        student.is_staff = True
        student.save(using=self._db)
        return student


class AppointmentManager(models.Manager):
    def upcoming(self):
        return self.filter(dt__gte=Now())
