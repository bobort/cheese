from decimal import Decimal

from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Sum, F, Q
from django.urls import reverse
from django.utils import timezone
from tinymce.models import HTMLField

from profile.managers import StudentManager, OrderLineItemQuerySet, AvailableProductsManager

USMLE_STEP1, USMLE_STEP2CK, USMLE_STEP2CS, USMLE_STEP3, COMLEX_LEVEL1, COMLEX_LEVEL2, COMLEX_LEVEL3, \
SPECIALTY, MED_COACH_A, MED_COACH_B, OTHER, ALL = range(0, 12)

EXAM_CHOICES = (
    (COMLEX_LEVEL1, "COMLEX Level 1"),
    (COMLEX_LEVEL2, "COMLEX Level 2"),
    (COMLEX_LEVEL3, "COMLEX Level 3"),
    (MED_COACH_A, "Medical School Year 1 & 2 Coaching"),
    (MED_COACH_B, "Medical School Year 3 & 4 Coaching"),
    (SPECIALTY, "Specialty Board Certification"),
    (USMLE_STEP1, "USMLE Step 1"),
    (USMLE_STEP2CK, "USMLE Step 2CK"),
    (USMLE_STEP3, "USMLE Step 3"),
    (OTHER, "Other"),
    (ALL, "All"),
)


class Student(AbstractUser):
    MD, DO = range(0, 2)
    DEGREE_CHOICES = (
        (MD, "MD"),
        (DO, "DO"),
    )
    username = None
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateField()
    last_login = models.DateTimeField()
    institution = models.CharField(max_length=255, blank=True, null=True, verbose_name="School Name")
    balance_paid = models.BooleanField(default=False, blank=True, null=True)
    graduation_year = models.IntegerField(
        blank=False,
        null=True,
        help_text="Enter all 4 digits. If you haven't graduated yet, enter the year you expect to graduate.",
        validators=(
            MinValueValidator(1900),
            MaxValueValidator(2050)
        )
    )
    degree = models.IntegerField(choices=DEGREE_CHOICES, blank=False, null=True, help_text="MD or DO")
    exam = models.IntegerField(
        blank=False,
        null=True,
        choices=EXAM_CHOICES,
        help_text="Choose the exam you are preparing for."
    )
    test_date = models.DateField(
        blank=True,
        null=True,
        help_text="Enter the date that you need to complete the test by or the date you are scheduled to take it."
    )
    phone_number = models.CharField(max_length=31, blank=False, null=True)
    marketing_subscription = models.BooleanField(default=True, verbose_name="Agree to receive marketing emails")
    # Account balance tracking
    account_balance = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        help_text="Current outstanding balance on account"
    )
    # Stripe subscription fields
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True, help_text="Stripe Customer ID")
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True, help_text="Stripe Subscription ID for balance payments")
    stripe_payment_method_id = models.CharField(max_length=255, blank=True, null=True, help_text="Stripe Payment Method ID")
    subscription_active = models.BooleanField(default=False, help_text="Whether subscription is currently active")
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    objects = StudentManager()

    class Meta:
        verbose_name = "Student"
        ordering = ('last_name', )


    @property
    def current_balance(self):
        """Calculate current balance from orders"""
        # Sum of all order totals (what student owes)
        total_owed = self.order_set.all().aggregate(
            sum=Sum('grand_total')
        )['sum'] or Decimal('0.00')
        
        # Sum of all payments made (orders with date_paid)
        total_paid = self.order_set.filter(
            date_paid__isnull=False
        ).aggregate(
            sum=Sum('grand_total')
        )['sum'] or Decimal('0.00')
        
        # Balance = what's owed - what's been paid
        # Positive balance means student owes money
        return total_owed - total_paid
    
    def update_account_balance(self):
        """Update the account_balance field from calculated balance"""
        self.account_balance = self.current_balance
        self.balance_paid = (self.account_balance <= 0)
        self.save(update_fields=['account_balance', 'balance_paid'])

    @property
    def ocean_courage_subscription(self):
        class SubscriptionInformation(object):
            expiration = None

            def __init__(s, expiration):
                s.expiration = expiration

            @property
            def is_expired(s):
                return s.expiration < timezone.now().date() if s.expiration else False

        ocs = self.productuser_set.filter(product__name="Ocean Courage Drill Sessions")
        if ocs:
            si = SubscriptionInformation(max([oc.product_end_date for oc in ocs]))
            return si
        return None

    @property
    def can_access_drills(self):
        return self.productuser_set.filter(
            Q(product_end_date__gte=timezone.now().date()) | Q(product_end_date__isnull=True),
            product__name="Ocean Courage Drill Sessions",
        ).exists()

    def __str__(self):
        return self.get_full_name()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.date_joined = timezone.now()
            self.last_login = timezone.now()
        return super().save(*args, **kwargs)

    def get_full_name(self):
        return f"{self.last_name}, {self.first_name}"

    def get_absolute_url(self):
        return reverse('profile:view', kwargs={'pk': self.pk})


class Testimonial(models.Model):
    testimonial = HTMLField()
    citation = models.CharField(max_length=255)

    class Meta:
        ordering = ('-pk', )


class Order(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date_paid = models.DateTimeField(default=timezone.now)
    number = models.CharField(max_length=7)
    total = models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)
    in_person_appt_qty = models.SmallIntegerField(blank=True, default=0, null=True, verbose_name='In Person Appointments')
    remote_appt_qty = models.SmallIntegerField(blank=True, default=0, null=True, verbose_name='Online Appointments')

    def __str__(self):
        return f"{self.student} ({self.date_paid}): Paid ${self.grand_total}"

    def get_absolute_url(self):
        return reverse('profile:receipt', kwargs={'pk': self.pk})

    @classmethod
    def get_next_number(cls):
        current_year = timezone.now().year
        orders_this_year = cls.objects.filter(date_paid__year=current_year).count() or 0
        return f"{str(current_year)[2:]}-{(orders_this_year + 1):04d}"

    @property
    def grand_total(self):
        return self.orderlineitem_set.aggregate(
            s=Sum(F('charge') * F('qty'), output_field=models.FloatField())
        )['s'] or 0

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = Order.get_next_number()
        if self.student:
            self.student.balanced_paid = False
            self.student.save()
        result = super().save(*args, **kwargs)
        return result


class OrderLineItem(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    product_start_date = models.DateField(blank=True, null=True)
    product_end_date = models.DateField(blank=True, null=True)
    qty = models.SmallIntegerField(verbose_name="Quantity")
    # since charges may change over time, save in Order
    charge = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Charge (USD)")
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    objects = OrderLineItemQuerySet.as_manager()

    @property
    def total_charge(self):
        return Decimal(self.qty) * self.charge

    def __str__(self):
        return f"{self.product.name} x{self.qty} @ ${self.charge}; {self.order.student} on {self.order.date_paid}"


class Product(models.Model):
    name = models.CharField(max_length=255)
    notes = models.TextField(blank=True, null=True)
    product_duration = models.DurationField(blank=True, null=True)
    account_name = models.CharField(max_length=255)
    # TODO add ability to track all exams for a particular product so that
    #    we can render only the products that a student would find helpful
    #    based on the exam that they are taking
    charge = models.DecimalField(max_digits=6, decimal_places=2)  # track how much this product costs
    owners = models.ManyToManyField('Student', blank=True, related_name="products")
    expiration_date = models.DateField(blank=True, null=True)
    removed = models.BooleanField()

    objects = models.Manager()
    available = AvailableProductsManager()

    def __str__(self):
        return self.name

    @admin.display()
    def qty_ordered(self):
        return OrderLineItem.objects.filter(product=self.pk).count()


class Staff(Student):
    description = models.TextField()
    image_path = models.CharField(max_length=255)


class ProductUser(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Student, on_delete=models.CASCADE)
    product_start_date = models.DateField(blank=True, null=True)
    product_end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.product.name} {self.customer} {self.product_end_date}"


class StripePayment(models.Model):
    """Track Stripe subscription payments for account balance"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='stripe_payments')
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True, help_text="Stripe Payment Intent ID")
    stripe_invoice_id = models.CharField(max_length=255, blank=True, null=True, help_text="Stripe Invoice ID")
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount paid in USD")
    status = models.CharField(
        max_length=50,
        choices=[
            ('pending', 'Pending'),
            ('succeeded', 'Succeeded'),
            ('failed', 'Failed'),
            ('canceled', 'Canceled'),
        ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional Stripe metadata")

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.student} - ${self.amount} - {self.status} ({self.created_at})"
