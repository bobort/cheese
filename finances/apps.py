from django.apps import AppConfig


class RegistrationConfig(AppConfig):
    name = 'finances'

    def ready(self):
        from . import signals  # noqa


