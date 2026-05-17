"""
Dispensing and prescription models.
"""
from django.db import models

from apps.core.models import NPTTEBaseModel
from apps.organisations.models import Organisation
from apps.patients.models import PatientProfile
from apps.products.models import Product
from apps.serialization.models import ProductSerial


class PrescriptionUpload(NPTTEBaseModel):
    """Uploaded prescription reference for validation and dispensing linkage."""

    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="prescription_uploads",
    )
    pharmacy = models.ForeignKey(
        Organisation,
        on_delete=models.PROTECT,
        related_name="prescription_uploads",
    )
    file_reference = models.CharField(
        max_length=512,
        help_text="Secure storage path or object key for the prescription document.",
    )
    prescriber_name = models.CharField(max_length=255, blank=True)
    issued_at = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Prescription upload"
        verbose_name_plural = "Prescription uploads"

    def __str__(self):
        return f"Prescription {self.id}"


class DispensingTransaction(NPTTEBaseModel):
    """Medicine dispensing event at a licensed pharmacy or facility."""

    pharmacy = models.ForeignKey(
        Organisation,
        on_delete=models.PROTECT,
        related_name="dispensing_transactions",
    )
    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dispensing_transactions",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="dispensing_transactions",
    )
    product_serial = models.ForeignKey(
        ProductSerial,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dispensing_transactions",
    )
    prescription = models.ForeignKey(
        PrescriptionUpload,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dispensing_transactions",
    )
    quantity_dispensed = models.PositiveIntegerField(default=1)
    dispensed_at = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ["-dispensed_at"]
        verbose_name = "Dispensing transaction"
        verbose_name_plural = "Dispensing transactions"

    def __str__(self):
        return f"Dispense {self.id} — {self.product}"
