from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Sum
from django.utils import timezone

from profile.managers import StudentManager

STEP1, STEP2CK, STEP2CS, STEP3, SPECIALTY, OTHER = range(0, 6)
EXAM_CHOICES = (
    (STEP1, "USMLE Step 1"),
    (STEP2CK, "USMLE Step 2CK"),
    (STEP2CS, "USMLE Step 2CS"),
    (STEP3, "USMLE Step 3"),
    (SPECIALTY, "USMLE Specialty Board Certification"),
    (OTHER, "Other"),
)


class Student(AbstractUser):
    MD, DO = range(0, 2)
    DEGREE_CHOICES = (
        (MD, "M.D."),
        (DO, "D.O."),
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
    degree = models.IntegerField(choices=DEGREE_CHOICES, blank=False, null=True, help_text="M.D. or D.O.")
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
    IN_PERSON, REMOTE = range(0, 2)
    TYPE_CHOICES = (
        (IN_PERSON, "In Person"),
        (REMOTE, "Remote Video Conference"),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    dt = models.DateTimeField()
    duration = models.DurationField()
    charge = models.DecimalField(max_digits=6, decimal_places=2)  # track how much this appointment cost the student
    location = models.CharField(max_length=255, blank=True, null=True)
    type = models.IntegerField(choices=TYPE_CHOICES)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student}: {self.dt} for {self.duration} charged ${self.charge}"


class Payment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date_paid = models.DateTimeField(default=timezone.now)
    total = models.DecimalField(max_digits=6, decimal_places=2)
    in_person_appt_qty = models.PositiveSmallIntegerField(default=0, verbose_name="Appointments In Person")
    remote_appt_qty = models.PositiveSmallIntegerField(default=0, verbose_name="Appointments Remotely")

    def __str__(self):
        return f"{self.student} ({self.date_paid}): Paid ${self.total}"
