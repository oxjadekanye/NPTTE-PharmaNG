from django.contrib import admin

from apps.regulatory.models import RegulatoryAlert


@admin.register(RegulatoryAlert)
class RegulatoryAlertAdmin(admin.ModelAdmin):
    list_display = ("title", "severity", "organisation", "alert_type", "status", "created_at")
    list_filter = ("severity", "alert_type", "status")
    search_fields = ("title", "description")
