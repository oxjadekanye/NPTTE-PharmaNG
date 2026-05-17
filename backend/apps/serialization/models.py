"""
Serial number and QR identity models.
"""
from django.db import models

from apps.core.models import NPTTEBaseModel
from apps.products.models import ProductBatch


class ProductSerial(NPTTEBaseModel):
    """
    Unique serialised unit identity for a medicine pack.

    Foundation for QR verification and supply chain event correlation.
    """

    batch = models.ForeignKey(
        ProductBatch,
        on_delete=models.PROTECT,
        related_name="serials",
    )
    serial_number = models.CharField(max_length=128, unique=True, db_index=True)
    qr_payload = models.CharField(
        max_length=512,
        blank=True,
        help_text="Encoded QR payload or URL reference for public verification.",
    )
    is_dispensed = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["serial_number"]
        verbose_name = "Product serial"
        verbose_name_plural = "Product serials"

    def __str__(self):
        return self.serial_number
