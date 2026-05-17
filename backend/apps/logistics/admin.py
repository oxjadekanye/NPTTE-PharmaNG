from django.contrib import admin

from apps.logistics.models import LogisticsProviderProfile, LogisticsShipment


@admin.register(LogisticsProviderProfile)
class LogisticsProviderProfileAdmin(admin.ModelAdmin):
    list_display = ("organisation", "transport_license", "fleet_size", "is_active")


@admin.register(LogisticsShipment)
class LogisticsShipmentAdmin(admin.ModelAdmin):
    list_display = (
        "tracking_number",
        "origin_organisation",
        "destination_organisation",
        "departed_at",
        "delivered_at",
    )
    search_fields = ("tracking_number",)
