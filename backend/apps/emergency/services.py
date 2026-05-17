"""Emergency medicine monitoring services."""
from __future__ import annotations

from decimal import Decimal

from django.db.models import Sum

from apps.core.constants import AlertCategory, AlertSeverity
from apps.emergency.models import EmergencyMedicineWatchlist
from apps.inventory.models import InventoryItem


def check_emergency_stock_levels() -> list[dict]:
    """Evaluate watchlist products against national stock thresholds."""
    alerts = []
    for entry in EmergencyMedicineWatchlist.objects.filter(is_active_watch=True, is_active=True):
        total = (
            InventoryItem.objects.filter(product=entry.product, is_active=True).aggregate(
                t=Sum("quantity_on_hand")
            )["t"]
            or 0
        )
        if total < entry.minimum_national_stock:
            from apps.alerts.services import create_national_alert

            create_national_alert(
                alert_type=AlertCategory.SHORTAGE,
                title=f"Emergency shortage: {entry.product.name}",
                description=f"National stock {total} below minimum {entry.minimum_national_stock}.",
                severity=AlertSeverity.CRITICAL,
                risk_score=Decimal("95"),
                product=entry.product,
                evidence_payload={"national_stock": total, "minimum": entry.minimum_national_stock},
            )
            alerts.append({"product": entry.product.name, "national_stock": total})
    return alerts
