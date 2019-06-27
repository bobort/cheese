from django.conf import settings
from django.core.mail import EmailMessage


def send_html_email(subject, html_message, recipients, sender=None):
    if not sender:
        sender = "no-reply@oceanink.net"
    if recipients:
        if settings.DEBUG:
            subject = f"[Ocean Ink Dev] {subject}"
            html_message = f"Normally sent to: {list(recipients)}<br><br>{html_message}"
            recipients = [admin_tuple[1] for admin_tuple in settings.ADMINS]
        else:
            subject = f"[Ocean Ink] {subject}"
        email_message = EmailMessage(subject, html_message, sender, recipients)
        email_message.content_subtype = "html"
        email_message.send()


def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]
