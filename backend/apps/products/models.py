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
