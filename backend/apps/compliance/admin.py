from django.contrib import admin

from apps.compliance.models import ComplianceRecord


@admin.register(ComplianceRecord)
class ComplianceRecordAdmin(admin.ModelAdmin):
    list_display = ("organisation", "regulator_code", "compliance_type", "is_compliant", "assessed_at")
    list_filter = ("regulator_code", "is_compliant")
