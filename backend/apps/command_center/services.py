"""National Command Center intelligence service."""
from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from django.db.models import Avg, Count
from django.utils import timezone

from apps.alerts.models import NationalAlert
from apps.command_center.models import (
    EmergencyIntervention,
    NationalIncident,
    NationalThreatAssessment,
    RegionalHealthSignal,
    SupplyChainDisruption,
)
from apps.core.cache import cache_get, cache_set, dashboard_cache_key
from apps.core.constants import AlertCategory, IncidentStatus, VerificationOutcome
from apps.national_dashboard.services import NationalCommandMetricsService
from apps.verification.models import VerificationScanLog


class NationalCommandService:
    """Enterprise national command operations — regulator-grade aggregation."""

    @staticmethod
    def live_overview() -> dict:
        key = dashboard_cache_key("command_live_overview")
        cached = cache_get(key)
        if cached:
            return cached
        base = NationalCommandMetricsService.national_overview()
        data = {
            **base,
            "open_incidents": NationalIncident.objects.filter(
                status__in=[IncidentStatus.OPEN, IncidentStatus.INVESTIGATING], is_active=True
            ).count(),
            "active_disruptions": SupplyChainDisruption.objects.filter(is_active_disruption=True).count(),
            "active_interventions": EmergencyIntervention.objects.filter(
                resolved_at__isnull=True, is_active=True
            ).count(),
            "national_threat": NationalCommandService._latest_threat_score(),
        }
        cache_set(key, data, timeout=60)
        return data

    @staticmethod
    def threat_map() -> dict:
        hotspots = list(
            VerificationScanLog.objects.filter(
                outcome=VerificationOutcome.COUNTERFEIT_SUSPECTED,
                latitude__isnull=False,
            )
            .values("latitude", "longitude", "serial_number")
            .annotate(scan_count=Count("id"))[:500]
        )
        regional = list(
            RegionalHealthSignal.objects.filter(created_at__gte=timezone.now() - timedelta(days=7))
            .values("state")
            .annotate(avg_risk=Avg("risk_score"))
        )
        return {"counterfeit_hotspots": hotspots, "regional_signals": regional}

    @staticmethod
    def active_incidents() -> dict:
        incidents = NationalIncident.objects.filter(
            status__in=[IncidentStatus.OPEN, IncidentStatus.INVESTIGATING], is_active=True
        ).select_related("organisation", "product")[:100]
        return {
            "incidents": [
                {
                    "id": str(i.id),
                    "code": i.incident_code,
                    "title": i.title,
                    "severity": i.severity,
                    "status": i.status,
                    "threat_score": str(i.threat_score),
                    "states": i.affected_states,
                }
                for i in incidents
            ]
        }

    @staticmethod
    def emergency_response() -> dict:
        interventions = EmergencyIntervention.objects.filter(resolved_at__isnull=True).order_by(
            "-activated_at"
        )[:50]
        shortage_alerts = NationalAlert.objects.filter(
            alert_type=AlertCategory.SHORTAGE, resolved_at__isnull=True
        ).count()
        return {
            "interventions": [
                {
                    "code": e.intervention_code,
                    "title": e.title,
                    "priority": e.priority_level,
                    "states": e.target_states,
                }
                for e in interventions
            ],
            "open_shortage_alerts": shortage_alerts,
        }

    @staticmethod
    def regional_risk() -> dict:
        signals = (
            RegionalHealthSignal.objects.filter(recorded_at__gte=timezone.now() - timedelta(days=30))
            .values("state")
            .annotate(avg_risk=Avg("risk_score"), signal_count=Count("id"))
            .order_by("-avg_risk")[:37]
        )
        return {"states": list(signals)}

    @staticmethod
    def _latest_threat_score() -> str:
        latest = NationalThreatAssessment.objects.order_by("-created_at").first()
        return str(latest.national_risk_score) if latest else "0"

    @staticmethod
    def refresh_threat_assessment() -> NationalThreatAssessment:
        """Heuristic national threat rollup for command center."""
        counterfeit = VerificationScanLog.objects.filter(
            outcome=VerificationOutcome.COUNTERFEIT_SUSPECTED,
            created_at__gte=timezone.now() - timedelta(days=7),
        ).count()
        shortage = NationalAlert.objects.filter(alert_type=AlertCategory.SHORTAGE).count()
        score = min(Decimal(counterfeit * 2 + shortage * 3), Decimal("100"))
        return NationalThreatAssessment.objects.create(
            assessment_period="rolling_7d",
            national_risk_score=score,
            counterfeit_risk=min(Decimal(counterfeit * 3), Decimal("100")),
            shortage_risk=min(Decimal(shortage * 5), Decimal("100")),
            diversion_risk=Decimal("0"),
        )
