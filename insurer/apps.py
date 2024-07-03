from django.apps import AppConfig


class InsurerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'insurer'

    def ready(self):
        import insurer.signals
