from django.apps import AppConfig


class StreambusConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.streambus"
    verbose_name = "Operational Event Bus"
