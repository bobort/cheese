from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import get_template

from profile.models import Student, Order


@receiver(post_save, sender=Student)
def post_save_student(sender, instance, created, **kwargs):
    if created:
        message = get_template('email.html').render({'student': instance})
        send_mail(
            "[Ocean Ink] New Student", message, "mouser@oceanink.net",
            ["matthew.pava@gmail.com", "drlepava@gmail.com"], True,
            html_message=message
        )
        message = get_template('email_welcome.html').render({'user': instance})
        send_mail(
            "[Ocean Ink] Welcome", message, "drlepava@gmail.com",
            [instance.email], True,
            html_message=message
        )


@receiver(post_save, sender=Order)
def post_save_order(sender, instance, created, **kwargs):
    if created:
        message = get_template('email_receipt.html').render({'order': instance})
        send_mail(
            "[Ocean Ink] Thank you for your payment.", message, "matthew.pava@gmail.com",
            [instance.student.email], True,
            html_message=message
        )
