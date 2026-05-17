from django.contrib import admin

from apps.traceability.models import BatchRecall, SupplyChainTransaction


@admin.register(SupplyChainTransaction)
class SupplyChainTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "audit_reference",
        "transaction_type",
        "source_organisation",
        "destination_organisation",
        "product",
        "quantity_delta",
        "verification_status",
        "risk_level",
        "created_at",
    )
    list_filter = ("transaction_type", "verification_status", "risk_level", "created_at")
    search_fields = ("audit_reference", "notes", "product__name")
    readonly_fields = (
        "id",
        "audit_reference",
        "is_immutable",
        "created_at",
        "updated_at",
        "device_metadata",
        "product_metadata",
        "batch_metadata",
    )
    date_hierarchy = "created_at"

    def has_change_permission(self, request, obj=None):
        if obj and obj.is_immutable:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(BatchRecall)
class BatchRecallAdmin(admin.ModelAdmin):
    list_display = ("batch", "effective_at", "resolved_at", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("batch__batch_number", "recall_reason")
