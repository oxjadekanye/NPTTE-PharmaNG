from django.contrib import admin

from apps.alerts.models import NationalAlert


@admin.register(NationalAlert)
class NationalAlertAdmin(admin.ModelAdmin):
    list_display = ("title", "alert_type", "severity", "risk_level", "state", "created_at")
    list_filter = ("alert_type", "severity", "risk_level", "state")
    search_fields = ("title", "description")
