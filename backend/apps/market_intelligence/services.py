"""National medicine market intelligence — heuristic analytics."""
from __future__ import annotations

from decimal import Decimal

from django.db.models import Avg
from django.utils import timezone

from apps.market_intelligence.models import MarketShortageSignal, MedicinePriceIndex, PriceManipulationAlert


def detect_price_manipulation(*, product_id, state: str, threshold_percent: Decimal = Decimal("35")) -> bool:
    indices = MedicinePriceIndex.objects.filter(product_id=product_id, state=state).order_by("-recorded_at")[:5]
    if len(indices) < 2:
        return False
    latest = indices[0]
    if latest.reference_price <= 0:
        return False
    spike = ((latest.observed_price - latest.reference_price) / latest.reference_price) * 100
    if spike >= threshold_percent:
        PriceManipulationAlert.objects.create(
            product_id=product_id,
            spike_percent=spike,
            created_at=timezone.now(),
        )
        return True
    return False


def calculate_market_pressure(*, product_id, state: str) -> Decimal:
    """Regional medicine affordability and shortage pressure score."""
    from apps.core.constants import AvailabilityStatus
    from apps.inventory.models import InventoryItem

    low_stock = InventoryItem.objects.filter(
        product_id=product_id,
        organisation__state=state,
        availability_status__in=[AvailabilityStatus.LOW_STOCK, AvailabilityStatus.OUT_OF_STOCK],
    ).count()
    variance = MedicinePriceIndex.objects.filter(product_id=product_id, state=state).aggregate(
        avg_obs=Avg("observed_price"), avg_ref=Avg("reference_price")
    )
    pressure = Decimal(low_stock * 10)
    if variance["avg_ref"] and variance["avg_obs"]:
        ratio = (variance["avg_obs"] / variance["avg_ref"]) - 1
        pressure += min(Decimal(str(ratio)) * 50, Decimal("50"))
    pressure = min(pressure, Decimal("100"))
    MarketShortageSignal.objects.update_or_create(
        product_id=product_id,
        state=state,
        defaults={"pressure_score": pressure, "detected_at": timezone.now()},
    )
    return pressure
