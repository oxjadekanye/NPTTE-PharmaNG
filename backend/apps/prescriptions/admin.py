from django.contrib import admin

from apps.prescriptions.models import Prescription


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = (
        "prescription_number",
        "patient",
        "product",
        "issued_at",
        "is_fulfilled",
        "status",
    )
    list_filter = ("is_fulfilled", "status")
    search_fields = ("prescription_number",)
