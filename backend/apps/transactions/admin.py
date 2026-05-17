from django.contrib import admin

from apps.transactions.models import DispensingTransaction, PrescriptionUpload


@admin.register(PrescriptionUpload)
class PrescriptionUploadAdmin(admin.ModelAdmin):
    list_display = ("pharmacy", "patient", "issued_at", "status", "created_at")
    list_filter = ("status",)


@admin.register(DispensingTransaction)
class DispensingTransactionAdmin(admin.ModelAdmin):
    list_display = ("pharmacy", "product", "quantity_dispensed", "dispensed_at", "status")
    list_filter = ("status",)
    search_fields = ("product__name", "pharmacy__legal_name")
