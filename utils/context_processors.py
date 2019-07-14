from django.conf import settings


def add_context_data(request):
    return {
        'AUTHORIZE_NET_ENDPOINT': settings.AUTHORIZE_NET_ENDPOINT,
    }
