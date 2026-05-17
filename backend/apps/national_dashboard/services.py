"""National Command Center metrics aggregation."""
from __future__ import annotations

from django.db.models import Count, Sum
from datetime import timedelta

from django.utils import timezone

from apps.alerts.models import NationalAlert
from apps.analytics.services import national_inventory_summary, state_inventory_breakdown
from apps.core.cache import cache_get, cache_set, dashboard_cache_key
from apps.core.constants import AlertCategory, VerificationOutcome
from apps.fraud_detection.models import FraudRiskFlag
from apps.organisations.models import Organisation
from apps.traceability.models import SupplyChainTransaction
from apps.verification.models import VerificationScanLog


class NationalCommandMetricsService:
    """Regulator command center intelligence — cache-ready aggregation."""

    @staticmethod
    def national_overview() -> dict:
        key = dashboard_cache_key("national_overview")
        cached = cache_get(key)
        if cached:
            return cached
        data = {
            "inventory": national_inventory_summary(),
            "open_alerts": NationalAlert.objects.filter(resolved_at__isnull=True, is_active=True).count(),
            "unresolved_fraud_flags": FraudRiskFlag.objects.filter(is_resolved=False).count(),
            "high_risk_transactions": SupplyChainTransaction.objects.filter(
                risk_level__in=["high", "critical"]
            ).count(),
            "verification_scans_24h": VerificationScanLog.objects.filter(
                created_at__gte=timezone.now() - timedelta(hours=24)
            ).count(),
        }
        cache_set(key, data, timeout=120)
        return data

    @staticmethod
    def counterfeit_map() -> dict:
        scans = (
            VerificationScanLog.objects.filter(
                outcome=VerificationOutcome.COUNTERFEIT_SUSPECTED,
                latitude__isnull=False,
                longitude__isnull=False,
            )
            .values("latitude", "longitude")
            .annotate(count=Count("id"))[:500]
        )
        return {"hotspots": list(scans)}

    @staticmethod
    def shortages() -> dict:
        from apps.core.constants import AvailabilityStatus
        from apps.inventory.models import InventoryItem

        low = InventoryItem.objects.filter(
            availability_status__in=[AvailabilityStatus.LOW_STOCK, AvailabilityStatus.OUT_OF_STOCK],
            is_active=True,
        ).select_related("product", "organisation")[:100]
        return {
            "shortage_locations": [
                {
                    "organisation": i.organisation.legal_name,
                    "state": i.organisation.state,
                    "product": i.product.name,
                    "quantity": i.quantity_on_hand,
                    "status": i.availability_status,
                }
                for i in low
            ]
        }

    @staticmethod
    def supply_chain() -> dict:
        volumes = (
            SupplyChainTransaction.objects.values("transaction_type")
            .annotate(count=Count("id"))
            .order_by("-count")[:15]
        )
        return {"movement_volumes": list(volumes)}

    @staticmethod
    def high_risk_organisations() -> dict:
        orgs = (
            Organisation.objects.filter(fraud_flags__is_resolved=False)
            .annotate(flag_count=Count("fraud_flags"))
            .order_by("-flag_count")[:25]
        )
        return {
            "organisations": [
                {"id": str(o.id), "name": o.legal_name, "state": o.state, "flags": o.flag_count}
                for o in orgs
            ]
        }

    @staticmethod
    def verification_traffic() -> dict:
        return {
            "by_outcome": list(
                VerificationScanLog.objects.values("outcome")
                .annotate(count=Count("id"))
                .order_by("-count")
            )
        }

    @staticmethod
    def state_analytics() -> dict:
        return {"states": state_inventory_breakdown()}
