from django.contrib import admin

from apps.fraud_detection.models import FraudRiskFlag


@admin.register(FraudRiskFlag)
class FraudRiskFlagAdmin(admin.ModelAdmin):
    list_display = ("flag_type", "risk_level", "risk_score", "organisation", "is_resolved", "created_at")
    list_filter = ("flag_type", "risk_level", "is_resolved")
    search_fields = ("description",)
