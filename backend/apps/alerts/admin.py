from django.contrib import admin

from apps.alerts.models import NationalAlert, NationalAlertEscalation


@admin.register(NationalAlert)
class NationalAlertAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "alert_type",
        "severity",
        "risk_level",
        "risk_score",
        "state",
        "escalation_level",
        "created_at",
    )
    list_filter = ("alert_type", "severity", "risk_level", "state")
    search_fields = ("title", "description")


@admin.register(NationalAlertEscalation)
class NationalAlertEscalationAdmin(admin.ModelAdmin):
    list_display = ("alert", "escalated_to", "escalated_at")
