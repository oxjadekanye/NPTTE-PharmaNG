from django.contrib import admin

from apps.serialization.models import ProductSerial


@admin.register(ProductSerial)
class ProductSerialAdmin(admin.ModelAdmin):
    list_display = ("serial_number", "batch", "is_dispensed", "status", "is_active")
    search_fields = ("serial_number", "qr_payload")
    list_filter = ("is_dispensed", "status", "is_active")
