from django.contrib import admin

from apps.verification.models import VerificationEvent, VerificationScanLog


@admin.register(VerificationEvent)
class VerificationEventAdmin(admin.ModelAdmin):
    list_display = ("product_serial", "channel", "is_authentic", "created_at")
    list_filter = ("channel", "is_authentic")


@admin.register(VerificationScanLog)
class VerificationScanLogAdmin(admin.ModelAdmin):
    list_display = ("serial_number", "outcome", "client_ip", "created_at")
    list_filter = ("outcome",)
    search_fields = ("serial_number", "device_fingerprint")
    date_hierarchy = "created_at"
