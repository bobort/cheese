import datetime

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import UserManager
from django.db import models
from django.db.models import F, When, Case, Value, CharField, DateField, Q
from django.db.models.functions import Now, TruncDate
from django.utils import timezone

from cheese.settings import OCEAN_COURAGE_PRODUCTS


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
        student.save()
        return student

    def create_superuser(self, email, password, **extra_fields):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        student = self.create_user(email, password, **extra_fields)
        student.is_superuser = True
        student.is_staff = True
        student.save()
        return student


class AppointmentManager(models.Manager):
    def upcoming(self):
        return self.filter(dt__gte=Now())


class AvailableProductsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            (Q(expiration_date__isnull=True) & Q(removed=False)) |
            (Q(removed=False) & Q(expiration_date__gte=TruncDate(Now())))
        )


class OrderLineItemQuerySet(models.QuerySet):
    def with_ocean_courage_subscription_information(self):
        minimum_date = datetime.date(month=6, day=2, year=2019)
        # lis = list(self.filter(product__name="Ocean Courage Drill Sessions").select_related('order'))
        # different scenarios:
        #   order qty n on one receipt
        #   order qty n on one receipt and qty m on one receipt before the first receipt subscription expires
        #   Course subscribers have six weeks

        # for each purchase date, get the expiration date (purchase date + qty in months)
        #   if the next purchase date is after the previous expiration date, disregard the previous purchase date
        #   otherwise add qty in months to the last expiration date
        # TODO incorporate product_end_date into expiration
        # TODO    Set product_start_date when order is placed
        # TODO    Set product_end_date when order is placed by adding the product_duration field
        # TODO    Add Ocean Courage Drill Sessions to Course product name
        product_criteria_1 = [Q(product__name__icontains=s) for s in OCEAN_COURAGE_PRODUCTS]
        product_criteria = Q()
        for c in product_criteria_1:
            product_criteria |= c

        lis = list(self.filter(product_criteria).select_related('order').annotate(
            interval_unit=Case(
                When(
                    product__name="Ocean Courage Drill Sessions",
                    then=Value("1 month")
                ),
                default=Value("6 weeks"),
                output_field=CharField()
            )
        ).annotate(
            initial_date=Case(
                When(
                    order__date_paid__date__lt=minimum_date,
                    then=minimum_date
                ),
                When(
                    product_start_date__isnull=False,
                    then=F('product_start_date')
                ),
                default=F('order__date_paid__date'),
                output_field=DateField()
            )
        ).annotate(
            interval=F('qty')
        ).order_by('initial_date'))

        prev_li = None
        for li in lis:
            if li.interval_unit == "6 weeks":
                interval = relativedelta(weeks=6*li.interval)
            else:
                interval = relativedelta(months=li.interval)
            expiration_date = li.initial_date + interval
            if prev_li:
                if li.initial_date <= prev_li.expiration_date:
                    # add another day since access is still granted on the expiration date
                    expiration_date = prev_li.expiration_date + interval + relativedelta(days=1)
            li.expiration_date = expiration_date
            prev_li = li
        return lis
