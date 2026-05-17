"""
Medicine product master data models.
"""
from django.db import models

from apps.core.models import NPTTEBaseModel
from apps.organisations.models import Organisation


class Product(NPTTEBaseModel):
    """
    Registered medicine product in the national catalogue.

    Links to marketing authorisation holder and core pharmaceutical attributes.
    """

    name = models.CharField(max_length=255, db_index=True)
    brand_name = models.CharField(max_length=255, blank=True)
    active_ingredient = models.CharField(max_length=255, db_index=True)
    strength = models.CharField(max_length=64, blank=True)
    dosage_form = models.CharField(max_length=128, blank=True)
    pack_size = models.CharField(max_length=64, blank=True)
    national_product_code = models.CharField(
        max_length=128,
        blank=True,
        db_index=True,
        help_text="National or internal product identifier.",
    )
    reference_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="National reference retail price (NGN) for patient comparison.",
    )
    dosage_guidance = models.TextField(
        blank=True,
        help_text="Patient-facing dosage guidance summary.",
    )
    manufacturer = models.ForeignKey(
        Organisation,
        on_delete=models.PROTECT,
        related_name="manufactured_products",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return self.brand_name or self.name


class ProductBatch(NPTTEBaseModel):
    """Manufacturing or import batch for traceability and recall management."""

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="batches",
    )
    batch_number = models.CharField(max_length=128, db_index=True)
    manufacturing_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True, db_index=True)
    manufacturing_site = models.ForeignKey(
        "manufacturers.ManufacturingSite",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="batches",
    )
    serial_range_start = models.CharField(max_length=128, blank=True)
    serial_range_end = models.CharField(max_length=128, blank=True)
    quantity_produced = models.PositiveIntegerField(default=0)
    verification_hash = models.CharField(max_length=128, blank=True, db_index=True)
    regulator_status = models.CharField(
        max_length=32,
        default="pending",
        db_index=True,
        help_text="NAFDAC/regulator approval status for batch release.",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Product batch"
        verbose_name_plural = "Product batches"
        constraints = [
            models.UniqueConstraint(
                fields=["product", "batch_number"],
                name="unique_product_batch_number",
            ),
        ]

    def __str__(self):
        return f"{self.product} — {self.batch_number}"
