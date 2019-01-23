from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import get_template

from profile.models import Student, Payment


@receiver(post_save, sender=Student)
def post_save_student(sender, instance, **kwargs):
    message = get_template('email.html').render({'student': instance})
    send_mail(
        "[Ocean Ink] New Student", message, "mouser@oceanink.net", ["matthew.pava@gmail.com"], True,
        html_message=message
    )


@receiver(post_save, sender=Payment)
def post_save_payment(sender, instance, **kwargs):
    message = get_template('email_receipt.html').render({'payment': instance})
    send_mail(
        "[Ocean Ink] New Payment", message, "mouser@oceanink.net", ["matthew.pava@gmail.com"], True,
        html_message=message
    )

