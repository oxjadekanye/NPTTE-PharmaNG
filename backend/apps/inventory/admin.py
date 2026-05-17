from django.contrib import admin

from apps.inventory.models import InventoryItem, InventoryMovement


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = (
        "organisation",
        "product",
        "quantity_on_hand",
        "availability_status",
        "is_active",
    )
    list_filter = ("availability_status", "status", "is_active")
    search_fields = ("organisation__legal_name", "product__name")


@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    list_display = ("inventory_item", "movement_type", "quantity_delta", "created_at")
    list_filter = ("movement_type",)
