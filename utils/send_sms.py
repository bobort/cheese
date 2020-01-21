# Download the helper library from https://www.twilio.com/docs/python/install
from django.conf import settings
from twilio.rest import Client


def send(message):
    twilio = settings.TWILIO
    account_sid = twilio.get('account_sid')
    auth_token = twilio.get('auth_token')
    client = Client(account_sid, auth_token)
    if settings.DEBUG:
        message = f"TEST: {message}"
    return client.messages.create(
        body=message,
        from_=twilio.get('from_phone_number'),
        to=twilio.get('to_phone_number'),
    )
