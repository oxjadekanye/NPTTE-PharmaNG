from django.contrib import admin

from apps.manufacturers.models import ManufacturerProfile


@admin.register(ManufacturerProfile)
class ManufacturerProfileAdmin(admin.ModelAdmin):
    list_display = ("organisation", "gmp_certificate_number", "is_active", "status")
    search_fields = ("organisation__legal_name", "gmp_certificate_number")
