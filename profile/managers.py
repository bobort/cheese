import datetime

from django.apps import apps
from django.contrib.auth.models import UserManager
from django.db import models
from django.db.models import Case, When, F
from django.db.models.functions import Now, ExtractMonth
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


class OceanCourageManager(models.QuerySet):
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs).filter(name="Ocean Courage Group Sessions")

    def with_expiration_date(self):
        OrderLineItem = apps.get_model("profile", "OrderLineItem")
        minimum_date = datetime.date(month=6, day=2, year=2019)
        # TODO retrieve only the most recent order line item per student
        for li in OrderLineItem.objects.filter(product__in=self).select_related('order'):
            if li.order.date_paid <= minimum_date:
                initial_date = minimum_date
            else:
                date_paid = li.order.date_paid
                initial_date = datetime.date(month=date_paid.month, day=date_paid.day, year=date_paid.year)
            interval = li.qty
            li.expiration_date = datetime.date(
                month=initial_date.month + interval,
                day=initial_date.day,
                year=initial_date.year + 1 if initial_date == 12 else 1
            )

