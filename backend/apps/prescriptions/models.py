from django.db import models

from apps.core.models import NPTTEBaseModel
from apps.organisations.models import Organisation
from apps.patients.models import PatientProfile
from apps.products.models import Product


class Prescription(NPTTEBaseModel):
    """National prescription record (distinct from legacy PrescriptionUpload in transactions)."""

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
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="prescriptions",
    )
    dosage_instructions = models.TextField(blank=True)
    quantity_prescribed = models.PositiveIntegerField(default=1)
    issued_at = models.DateTimeField(db_index=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_fulfilled = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["-issued_at"]
        verbose_name = "Prescription"
        verbose_name_plural = "Prescriptions"
