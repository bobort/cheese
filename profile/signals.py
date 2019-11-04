from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import get_template
from django.utils import timezone

from profile.models import Student, OrderLineItem
from cheese.settings import OCEAN_COURAGE_PRODUCTS
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
        if instance.product.name in OCEAN_COURAGE_PRODUCTS:
            # send out an email when the order is made for the first time
            # also send it out when they ordered it earlier, but it expired and they are ordering it again

            send_message = True
            renewal = False
            # retrieve all order line items for this student
            # filter out the instance just saved
            lis = [
                li
                for li in OrderLineItem.objects.filter(
                    order__student=instance.order.student
                ).with_ocean_courage_subscription_information()
                if li.pk != instance.pk
            ]
            if lis:
                # if the latest expiration is before today, send out a message since it is a renewal
                latest_expiration = max([li.expiration_date for li in lis])
                if timezone.now() > latest_expiration:
                    renewal = True
                else:
                    send_message = False

            if send_message:
                message = get_template('email_oceancourage.html').render({'order': instance.order, 'renewal': renewal})
                email_list = list(
                    Group.objects.get(name="oceancouragegroup").user_set.all().values_list('email', flat=True)
                )
                email_list += list(
                    get_user_model().objects.filter(is_superuser=True).values_list('email', flat=True)
                )
                send_html_email("New Ocean Courage Student", message, email_list, "matthew.pava@gmail.com")
