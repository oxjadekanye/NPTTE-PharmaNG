from django.apps import AppConfig


class DeveloperAccessConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.developer_access"
    verbose_name = "Public API developer access"
