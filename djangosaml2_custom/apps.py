from django.apps import AppConfig


class Djangosaml2CustomConfig(AppConfig):
    name = 'djangosaml2_custom'

    def ready(self):
        import djangosaml2_custom.signals.handlers

