from django.apps import AppConfig


class RegistrationConfig(AppConfig):
    name = 'profile'

    def ready(self):
        from . import signals  # noqa


