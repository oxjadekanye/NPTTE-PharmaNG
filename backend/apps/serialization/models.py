"""
Serial number and QR identity models.
"""
from django.conf import settings
from django.db import models

from apps.core.models import NPTTEBaseModel
from apps.organisations.models import Organisation
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
    custody_organisation = models.ForeignKey(
        Organisation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="serials_in_custody",
        help_text="Last pharmacy or supply-chain node that received this serial (Phase 8).",
    )
    custody_updated_at = models.DateTimeField(null=True, blank=True)
    custody_updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="serial_custody_updates",
    )

    class Meta:
        ordering = ["serial_number"]
        verbose_name = "Product serial"
        verbose_name_plural = "Product serials"

    gtin14 = models.CharField(max_length=14, blank=True, db_index=True)
    gs1_element_string = models.CharField(max_length=512, blank=True)
    counterfeit_probability = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        db_index=True,
        help_text="Last computed counterfeit probability (0–100).",
    )
    packaging_unit = models.ForeignKey(
        "serialization.SerialPackagingUnit",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="serials",
    )

    def __str__(self):
        return self.serial_number


class SerialPackagingUnit(NPTTEBaseModel):
    """Carton / pallet / inner-pack aggregation for national serialization (Phase 10)."""

    LEVEL_ITEM = "item"
    LEVEL_INNER = "inner_pack"
    LEVEL_CARTON = "carton"
    LEVEL_PALLET = "pallet"
    LEVEL_CHOICES = [
        (LEVEL_ITEM, "Item"),
        (LEVEL_INNER, "Inner pack"),
        (LEVEL_CARTON, "Carton"),
        (LEVEL_PALLET, "Pallet"),
    ]

    batch = models.ForeignKey(
        ProductBatch,
        on_delete=models.CASCADE,
        related_name="packaging_units",
    )
    pack_code = models.CharField(max_length=128, unique=True, db_index=True)
    level = models.CharField(max_length=32, choices=LEVEL_CHOICES, db_index=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )
    serial_count = models.PositiveIntegerField(default=0)
    sscc = models.CharField(max_length=20, blank=True, db_index=True, help_text="GS1 SSCC when applicable.")

    class Meta:
        ordering = ["pack_code"]
        verbose_name = "Serial packaging unit"
        verbose_name_plural = "Serial packaging units"

    def __str__(self):
        return f"{self.pack_code} ({self.level})"


class SerialScanRecord(NPTTEBaseModel):
    """Per-scan history for duplicate detection and forensic replay (Phase 10)."""

    product_serial = models.ForeignKey(
        ProductSerial,
        on_delete=models.CASCADE,
        related_name="scan_records",
        null=True,
        blank=True,
    )
    serial_number = models.CharField(max_length=128, db_index=True)
    scan_source = models.CharField(
        max_length=32,
        db_index=True,
        help_text="citizen, pharmacy, warehouse, customs, regulator",
    )
    scanner_type = models.CharField(max_length=32, blank=True, db_index=True)
    outcome = models.CharField(max_length=64, blank=True, db_index=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    device_fingerprint = models.CharField(max_length=64, blank=True, db_index=True)
    replay_nonce = models.CharField(max_length=64, blank=True, db_index=True)
    is_duplicate = models.BooleanField(default=False, db_index=True)
    is_suspicious = models.BooleanField(default=False, db_index=True)
    scan_metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["serial_number", "created_at"]),
            models.Index(fields=["replay_nonce"]),
        ]
