from django.contrib import admin

from apps.prescriptions.models import (
    DispensingRecord,
    PrescribingDoctor,
    Prescription,
    PrescriptionItem,
    RefillAuthorization,
)


@admin.register(PrescribingDoctor)
class PrescribingDoctorAdmin(admin.ModelAdmin):
    list_display = ("full_name", "license_number", "organisation")


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = (
        "prescription_number",
        "patient",
        "issued_at",
        "is_fulfilled",
        "risk_score",
        "is_controlled_substance",
    )
    list_filter = ("is_fulfilled", "is_controlled_substance")
    search_fields = ("prescription_number",)


@admin.register(PrescriptionItem)
class PrescriptionItemAdmin(admin.ModelAdmin):
    list_display = ("prescription", "product", "quantity")


@admin.register(DispensingRecord)
class DispensingRecordAdmin(admin.ModelAdmin):
    list_display = ("prescription", "pharmacy", "dispensed_at", "quantity_dispensed")


@admin.register(RefillAuthorization)
class RefillAuthorizationAdmin(admin.ModelAdmin):
    list_display = ("prescription", "authorized_refills", "refills_used")
