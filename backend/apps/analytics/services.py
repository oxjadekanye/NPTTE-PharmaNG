"""National pharmaceutical analytics aggregation services."""
from __future__ import annotations

from django.db.models import Count, Sum

from apps.core.constants import AvailabilityStatus
from apps.inventory.models import InventoryItem
from apps.organisations.models import Organisation
from apps.products.models import Product
from apps.traceability.models import SupplyChainTransaction


def national_inventory_summary() -> dict:
    qs = InventoryItem.objects.filter(is_active=True)
    return {
        "total_stock_units": qs.aggregate(total=Sum("quantity_on_hand"))["total"] or 0,
        "in_stock_locations": qs.filter(
            availability_status=AvailabilityStatus.IN_STOCK
        ).count(),
        "low_stock_locations": qs.filter(
            availability_status=AvailabilityStatus.LOW_STOCK
        ).count(),
        "out_of_stock_locations": qs.filter(
            availability_status=AvailabilityStatus.OUT_OF_STOCK
        ).count(),
    }


def transaction_volume_by_type() -> list[dict]:
    rows = (
        SupplyChainTransaction.objects.values("transaction_type")
        .annotate(count=Count("id"))
        .order_by("-count")[:20]
    )
    return list(rows)


def state_inventory_breakdown() -> list[dict]:
    return list(
        Organisation.objects.filter(inventory_items__is_active=True)
        .values("state")
        .annotate(
            organisations=Count("id", distinct=True),
            stock_units=Sum("inventory_items__quantity_on_hand"),
        )
        .order_by("-stock_units")[:37]
    )


def top_products_by_stock(limit: int = 10) -> list[dict]:
    return list(
        Product.objects.filter(inventory_items__is_active=True)
        .values("id", "name", "brand_name", "active_ingredient")
        .annotate(total_stock=Sum("inventory_items__quantity_on_hand"))
        .order_by("-total_stock")[:limit]
    )
