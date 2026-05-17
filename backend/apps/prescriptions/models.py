from django.db import models

from apps.core.models import NPTTEBaseModel
from apps.organisations.models import Organisation
from apps.patients.models import PatientProfile
from apps.products.models import Product
from apps.serialization.models import ProductSerial


class PrescribingDoctor(NPTTEBaseModel):
    """Licensed prescriber on the national platform."""

    full_name = models.CharField(max_length=255)
    license_number = models.CharField(max_length=128, unique=True, db_index=True)
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="prescribing_doctors",
    )
    specialty = models.CharField(max_length=128, blank=True)

    class Meta:
        verbose_name = "Prescribing doctor"
        verbose_name_plural = "Prescribing doctors"


class Prescription(NPTTEBaseModel):
    """National prescription record (e-prescription foundation)."""

    prescription_number = models.CharField(max_length=128, unique=True, db_index=True)
    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.PROTECT,
        related_name="prescriptions",
    )
    prescriber_organisation = models.ForeignKey(
        Organisation,
        on_delete=models.PROTECT,
        related_name="issued_prescriptions",
    )
    prescribing_doctor = models.ForeignKey(
        PrescribingDoctor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="prescriptions",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="prescriptions",
        null=True,
        blank=True,
    )
    dosage_instructions = models.TextField(blank=True)
    quantity_prescribed = models.PositiveIntegerField(default=1)
    issued_at = models.DateTimeField(db_index=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_fulfilled = models.BooleanField(default=False, db_index=True)
    is_controlled_substance = models.BooleanField(default=False, db_index=True)
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        ordering = ["-issued_at"]
        verbose_name = "Prescription"
        verbose_name_plural = "Prescriptions"


class PrescriptionItem(NPTTEBaseModel):
    """Line item on a national prescription."""

    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="prescription_items")
    quantity = models.PositiveIntegerField(default=1)
    dosage_instructions = models.TextField(blank=True)

    class Meta:
        verbose_name = "Prescription item"
        verbose_name_plural = "Prescription items"


class DispensingRecord(NPTTEBaseModel):
    """Pharmacy dispensing linked to prescription."""

    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.PROTECT,
        related_name="dispensing_records",
    )
    pharmacy = models.ForeignKey(
        Organisation,
        on_delete=models.PROTECT,
        related_name="prescription_dispensings",
    )
    product_serial = models.ForeignKey(
        ProductSerial,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dispensing_records",
    )
    quantity_dispensed = models.PositiveIntegerField(default=1)
    dispensed_at = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ["-dispensed_at"]
        verbose_name = "Dispensing record"
        verbose_name_plural = "Dispensing records"


class RefillAuthorization(NPTTEBaseModel):
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name="refill_authorizations",
    )
    authorized_refills = models.PositiveIntegerField(default=0)
    refills_used = models.PositiveIntegerField(default=0)
    last_refill_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Refill authorization"
        verbose_name_plural = "Refill authorizations"
