from django.contrib import admin

from apps.distributors.models import DistributorProfile


@admin.register(DistributorProfile)
class DistributorProfileAdmin(admin.ModelAdmin):
    list_display = ("organisation", "wholesale_license", "cold_chain_capable", "is_active")
    search_fields = ("organisation__legal_name",)
