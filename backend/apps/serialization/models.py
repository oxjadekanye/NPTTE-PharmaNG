"""
Serial number and QR identity models.
"""
from django.db import models

from apps.core.models import NPTTEBaseModel
from apps.products.models import Product, ProductBatch


class SerialSequence(NPTTEBaseModel):
    """Atomic national serial sequence counter per product per year."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="serial_sequences")
    year = models.PositiveIntegerField(db_index=True)
    last_sequence = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [("product", "year")]
        verbose_name = "Serial sequence"
        verbose_name_plural = "Serial sequences"


class ProductSerial(NPTTEBaseModel):
    """
    Unique serialised unit identity for a medicine pack (national BatchSerial registry).

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
    barcode_payload = models.CharField(max_length=128, blank=True, db_index=True)
    verification_hash = models.CharField(max_length=128, blank=True, db_index=True)
    qr_token_signature = models.CharField(max_length=128, blank=True)
    scan_count = models.PositiveIntegerField(default=0, db_index=True)
    is_dispensed = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["serial_number"]
        verbose_name = "Product serial"
        verbose_name_plural = "Product serials"

    def __str__(self):
        return self.serial_number
