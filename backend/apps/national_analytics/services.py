"""Nationwide pharmaceutical analytics aggregation."""
from __future__ import annotations

from datetime import timedelta

from django.db.models import Count, Sum
from django.utils import timezone

from apps.analytics.services import national_inventory_summary, state_inventory_breakdown
from apps.core.cache import cache_get, cache_set, dashboard_cache_key
from apps.core.constants import VerificationOutcome
from apps.traceability.models import SupplyChainTransaction
from apps.verification.models import VerificationScanLog


class NationalAnalyticsService:
    @staticmethod
    def national_summary() -> dict:
        key = dashboard_cache_key("national_analytics_summary")
        cached = cache_get(key)
        if cached:
            return cached
        data = {
            "inventory": national_inventory_summary(),
            "verification_24h": VerificationScanLog.objects.filter(
                created_at__gte=timezone.now() - timedelta(hours=24)
            ).count(),
            "transactions_7d": SupplyChainTransaction.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            ).count(),
        }
        cache_set(key, data, timeout=180)
        return data

    @staticmethod
    def heatmaps() -> dict:
        verification = list(
            VerificationScanLog.objects.filter(latitude__isnull=False)
            .values("latitude", "longitude", "outcome")
            .annotate(count=Count("id"))[:500]
        )
        transactions = list(
            SupplyChainTransaction.objects.filter(latitude__isnull=False)
            .values("latitude", "longitude", "transaction_type")
            .annotate(count=Count("id"))[:500]
        )
        return {"verification": verification, "supply_chain": transactions}

    @staticmethod
    def medicine_flow() -> dict:
        flow = (
            SupplyChainTransaction.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=30)
            )
            .values("transaction_type")
            .annotate(volume=Count("id"))
        )
        return {"flow_by_type": list(flow)}

    @staticmethod
    def risk_analysis() -> dict:
        counterfeit = VerificationScanLog.objects.filter(
            outcome=VerificationOutcome.COUNTERFEIT_SUSPECTED,
            created_at__gte=timezone.now() - timedelta(days=7),
        ).count()
        from apps.fraud_detection.models import FraudRiskFlag

        fraud = FraudRiskFlag.objects.filter(is_resolved=False).count()
        return {"counterfeit_scans_7d": counterfeit, "open_fraud_flags": fraud}

    @staticmethod
    def state_comparison() -> dict:
        return {"states": state_inventory_breakdown()}
