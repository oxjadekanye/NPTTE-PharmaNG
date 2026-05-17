from django.contrib import admin

from apps.manufacturers.models import (
    GMPComplianceRecord,
    ManufacturerProfile,
    ManufacturingAudit,
    ManufacturingSite,
    ProductionLicense,
    RecallNotice,
)


@admin.register(ManufacturerProfile)
class ManufacturerProfileAdmin(admin.ModelAdmin):
    list_display = ("organisation", "gmp_certificate_number", "compliance_score", "is_active")
    search_fields = ("organisation__legal_name",)


@admin.register(ManufacturingSite)
class ManufacturingSiteAdmin(admin.ModelAdmin):
    list_display = ("site_name", "site_code", "manufacturer", "state", "is_active")
    list_filter = ("state",)


@admin.register(ProductionLicense)
class ProductionLicenseAdmin(admin.ModelAdmin):
    list_display = ("license_number", "manufacturer", "expires_at")


@admin.register(GMPComplianceRecord)
class GMPComplianceRecordAdmin(admin.ModelAdmin):
    list_display = ("manufacturer", "inspection_date", "is_compliant", "score")


@admin.register(ManufacturingAudit)
class ManufacturingAuditAdmin(admin.ModelAdmin):
    list_display = ("manufacturer", "audit_type", "audited_at")


@admin.register(RecallNotice)
class RecallNoticeAdmin(admin.ModelAdmin):
    list_display = ("batch", "manufacturer", "effective_at", "resolved_at")
