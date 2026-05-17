"""
Stock and movement models.
"""
from django.db import models

from apps.core.constants import AvailabilityStatus
from apps.core.models import NPTTEBaseModel
from apps.organisations.models import Organisation
from apps.products.models import Product, ProductBatch


class InventoryItem(NPTTEBaseModel):
    """
    Stock position for a product (and optional batch) at an organisation location.

    Used by patient medication search to determine pharmacy availability.
    """

    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.PROTECT,
        related_name="inventory_items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="inventory_items",
    )
    batch = models.ForeignKey(
        ProductBatch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inventory_items",
    )
    quantity_on_hand = models.PositiveIntegerField(default=0)
    availability_status = models.CharField(
        max_length=32,
        choices=AvailabilityStatus.CHOICES,
        default=AvailabilityStatus.OUT_OF_STOCK,
        db_index=True,
    )
    last_restocked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Inventory item"
        verbose_name_plural = "Inventory items"
        indexes = [
            models.Index(fields=["organisation", "product", "availability_status"]),
        ]

    def __str__(self):
        return f"{self.organisation} — {self.product} ({self.quantity_on_hand})"


class InventoryMovement(NPTTEBaseModel):
    """Audit-friendly stock movement record (receipt, adjustment, dispense reserve)."""

    inventory_item = models.ForeignKey(
        InventoryItem,
        on_delete=models.PROTECT,
        related_name="movements",
    )
    movement_type = models.CharField(max_length=64, db_index=True)
    quantity_delta = models.IntegerField(
        help_text="Positive for stock in, negative for stock out.",
    )
    reference = models.CharField(max_length=128, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Inventory movement"
        verbose_name_plural = "Inventory movements"

    def __str__(self):
        return f"{self.movement_type}: {self.quantity_delta}"
