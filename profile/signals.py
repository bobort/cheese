from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import get_template

from profile.models import Student, OrderLineItem
from utils import send_html_email


@receiver(post_save, sender=Student)
def post_save_student(sender, instance, created, **kwargs):
    if created:
        message = get_template('email.html').render({'student': instance})
        send_html_email("New Student", message, ["matthew.pava@gmail.com", "drlepava@gmail.com"])
        message = get_template('email_welcome.html').render({'user': instance})
        send_html_email("Welcome", message, [instance.email], "drlepava@gmail.com")


@receiver(post_save, sender=OrderLineItem)
def post_save_orderlineitem(sender, instance, created, **kwargs):
    if created:
        if instance.product.name in ["Ocean Courage Group Sessions", "USMLE STEP2CK/3 & COMLEX LEVEL 2/3 Course"]:
            message = get_template('email_oceancourage.html').render({'order': instance})
            email_list = Group.objects.get(name="oceancouragegroup").user_set.all().values_list('email', flat=True)
            send_html_email("New Ocean Courage Student", message, email_list, "matthew.pava@gmail.com")

