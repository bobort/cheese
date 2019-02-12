from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Sum
from django.urls import reverse
from django.utils import timezone

from profile.managers import StudentManager

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
    (USMLE_STEP2CS, "USMLE Step 2CS"),
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
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    objects = StudentManager()

    class Meta:
        verbose_name = "Student"

    @property
    def exam_count(self):
        return self.examscore_set.filter(exam=self.exam).count()

    @property
    def current_balance(self):
        return self.payment_set.all().aggregate(sum=Sum('total'))['sum'] -\
               self.appointment_set.all().aggregate(sum=Sum('charge'))['sum']

    def __str__(self):
        return self.get_full_name()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.date_joined = timezone.now()
            self.last_login = timezone.now()
        return super().save(*args, **kwargs)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class ExamScore(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.IntegerField(choices=EXAM_CHOICES)
    score = models.IntegerField(
        validators=(
            MinValueValidator(1),
            MaxValueValidator(300),
        )
    )

    def __str__(self):
        return f"{self.student} {self.get_exam_display()}: {self.score}"


class Appointment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    dt = models.DateTimeField()
    duration = models.DurationField()
    location = models.CharField(max_length=255, blank=True, null=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student}: {self.dt} for {self.duration} ({self.product})charged ${self.product.charge}"


# TODO: rename this Order; add OrderLineItems model
class Payment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date_paid = models.DateTimeField(default=timezone.now)
    total = models.DecimalField(max_digits=6, decimal_places=2)
    in_person_appt_qty = models.SmallIntegerField(default=0, verbose_name="Appointments In Person")
    remote_appt_qty = models.SmallIntegerField(default=0, verbose_name="Appointments Remotely")
    order_number = models.CharField(max_length=7)

    def __str__(self):
        return f"{self.student} ({self.date_paid}): Paid ${self.total}"

    def get_absolute_url(self):
        return reverse('profile:receipt', kwargs={'pk': self.pk})

    @classmethod
    def get_next_order_number(cls):
        current_year = timezone.now().year
        orders_this_year = cls.objects.filter(date_paid__year=current_year).count() or 0
        return f"{str(current_year)[2:]}-{(orders_this_year + 1):04d}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = Payment.get_next_order_number()
        return super().save(*args, **kwargs)


class Product(models.Model):
    name = models.CharField(max_length=255)
    notes = models.TextField()
    # The exam that the product is designed for
    #   Even if you are not taking that exam, the list can be filtered to show every product available.
    exam = models.IntegerField(
        blank=False,
        null=True,
        choices=EXAM_CHOICES
    )
    charge = models.DecimalField(max_digits=6, decimal_places=2)  # track how much this product costs

