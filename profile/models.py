from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, MaxLengthValidator, MinValueValidator, MaxValueValidator
from django.db import models


from phonenumber_field.modelfields import PhoneNumberField


class ExamChoices(object):
    STEP1, STEP2CK, STEP2CS, STEP3, SPECIALTY, OTHER = range(0, 6)
    
    @classmethod
    def __call__(cls, *args, **kwargs):
        return (
            (cls.STEP1, "USMLE Step 1"),
            (cls.STEP2CK, "USMLE Step 2CK"),
            (cls.STEP2CS, "USMLE Step 2CS"),
            (cls.STEP3, "USMLE Step 3"),
            (cls.SPECIALTY, "USMLE Specialty Board Certification"),
            (cls.OTHER, "Other"),
        )


class Student(models.Model):
    MD, DO = range(0, 2)
    DEGREE_CHOICES = (
        (MD, "M.D."),
        (DO, "D.O."),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    f_name = models.CharField()
    l_name = models.CharField()
    graduation_year = models.IntegerField(
        help_text="Enter all 4 digits. If you haven't graduated yet, enter the year you expect to graduate.",
        validators=(
            MinLengthValidator(4),
            MaxLengthValidator(4)
        )
    )
    degree = models.IntegerField(choices=DEGREE_CHOICES)
    exam = models.IntegerField(
        choices=ExamChoices(),
        help_text="Choose the exam you are preparing for."
    )
    test_date = models.DateField(
        blank=True,
        null=True,
        help_text="Enter the date that you need to complete the test by or the date you are scheduled to take it."
    )
    phone_number = PhoneNumberField()

    @property
    def exam_count(self):
        return self.examscore_set.filter(exam=self.exam).count()


class ExamScore(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.IntegerField(choices=ExamChoices())
    score = models.IntegerField(
        validators=(
            MinValueValidator(1),
            MaxValueValidator(300),
        )
    )

