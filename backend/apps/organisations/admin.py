from django.contrib import admin

from apps.organisations.models import Organisation, OrganisationType


@admin.register(OrganisationType)
class OrganisationTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "status", "is_active", "created_at")
    search_fields = ("name", "code")
    list_filter = ("status", "is_active")


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = (
        "legal_name",
        "organisation_type",
        "state",
        "license_number",
        "status",
        "is_active",
    )
    search_fields = ("legal_name", "trading_name", "registration_number", "license_number")
    list_filter = ("organisation_type", "state", "status", "is_active")
