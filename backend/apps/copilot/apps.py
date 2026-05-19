from django.apps import AppConfig


class CopilotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.copilot"
    label = "copilot"
    verbose_name = "Intelligence copilot (Phase 20B)"
