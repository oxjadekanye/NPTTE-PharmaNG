from django.contrib import admin

from apps.distributors.models import DistributorProfile, Warehouse


@admin.register(DistributorProfile)
class DistributorProfileAdmin(admin.ModelAdmin):
    list_display = ("organisation", "wholesale_license", "cold_chain_capable", "risk_score")


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("name", "warehouse_code", "organisation", "state", "cold_chain_enabled")
