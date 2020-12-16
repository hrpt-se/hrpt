from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'apps.accounts'

    def ready(self):
        # When the app is ready, activate the signals defined in signals.py
        # by importing them.
        from . import signals
