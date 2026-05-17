from django.contrib import admin

from apps.pharmacies.models import PharmacyProfile


@admin.register(PharmacyProfile)
class PharmacyProfileAdmin(admin.ModelAdmin):
    list_display = (
        "organisation",
        "pharmacy_license_number",
        "supports_delivery",
        "status",
        "is_active",
    )
    search_fields = ("organisation__legal_name", "pharmacy_license_number")
    list_filter = ("supports_delivery", "supports_emergency_supply", "status", "is_active")
