from django.contrib import admin

from apps.logistics.models import (
    ColdChainLog,
    DeliveryConfirmation,
    LogisticsProviderProfile,
    LogisticsShipment,
    ShipmentCheckpoint,
    ShipmentItem,
    SmartWarehouse,
    TemperatureExcursion,
    WarehouseInventorySnapshot,
    WarehouseRiskAssessment,
    WarehouseZone,
)


@admin.register(LogisticsProviderProfile)
class LogisticsProviderProfileAdmin(admin.ModelAdmin):
    list_display = ("organisation", "transport_license", "fleet_size")


class ShipmentItemInline(admin.TabularInline):
    model = ShipmentItem
    extra = 0


@admin.register(LogisticsShipment)
class LogisticsShipmentAdmin(admin.ModelAdmin):
    list_display = (
        "tracking_number",
        "lifecycle_status",
        "origin_organisation",
        "destination_organisation",
        "departed_at",
    )
    list_filter = ("lifecycle_status",)
    inlines = [ShipmentItemInline]


@admin.register(ShipmentCheckpoint)
class ShipmentCheckpointAdmin(admin.ModelAdmin):
    list_display = ("shipment", "recorded_at", "latitude", "longitude")


@admin.register(DeliveryConfirmation)
class DeliveryConfirmationAdmin(admin.ModelAdmin):
    list_display = ("shipment", "confirmed_at", "quantity_received")


@admin.register(ColdChainLog)
class ColdChainLogAdmin(admin.ModelAdmin):
    list_display = ("shipment", "temperature_celsius", "is_breach", "recorded_at")
    list_filter = ("is_breach",)


admin.site.register(SmartWarehouse)
admin.site.register(WarehouseZone)
admin.site.register(WarehouseInventorySnapshot)
admin.site.register(TemperatureExcursion)
admin.site.register(WarehouseRiskAssessment)
