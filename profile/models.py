from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, MaxLengthValidator, MinValueValidator, MaxValueValidator
from django.db import models


from phonenumber_field.modelfields import PhoneNumberField


STEP1, STEP2CK, STEP2CS, STEP3, SPECIALTY, OTHER = range(0, 6)
EXAM_CHOICES = (
    (STEP1, "USMLE Step 1"),
    (STEP2CK, "USMLE Step 2CK"),
    (STEP2CS, "USMLE Step 2CS"),
    (STEP3, "USMLE Step 3"),
    (SPECIALTY, "USMLE Specialty Board Certification"),
    (OTHER, "Other"),
)


class Student(models.Model):
    MD, DO = range(0, 2)
    DEGREE_CHOICES = (
        (MD, "M.D."),
        (DO, "D.O."),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    graduation_year = models.IntegerField(
        help_text="Enter all 4 digits. If you haven't graduated yet, enter the year you expect to graduate.",
        validators=(
            MinValueValidator(1900),
            MaxValueValidator(2050)
        )
    )
    degree = models.IntegerField(choices=DEGREE_CHOICES, help_text="M.D. or D.O.")
    exam = models.IntegerField(
        choices=EXAM_CHOICES,
        help_text="Choose the exam you are preparing for."
    )
    test_date = models.DateField(
        blank=True,
        null=True,
        help_text="Enter the date that you need to complete the test by or the date you are scheduled to take it."
    )
    phone_number = models.CharField(max_length=31)

    @property
    def exam_count(self):
        return self.examscore_set.filter(exam=self.exam).count()


class ExamScore(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.IntegerField(choices=EXAM_CHOICES)
    score = models.IntegerField(
        validators=(
            MinValueValidator(1),
            MaxValueValidator(300),
        )
    )

