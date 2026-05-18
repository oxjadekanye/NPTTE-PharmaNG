"""Distributed operational telemetry aggregation."""
from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from django.db.models import Count
from django.utils import timezone

from apps.onboarding.models import OrganisationOnboarding
from apps.scanning.models import ScanEvent
from apps.streambus.constants import EVT_TELEMETRY
from apps.streambus.models import EventLifecycleLog, OperationalTelemetrySnapshot
from apps.streambus.services.bus import publish_operational_event
from apps.traceability.models import RecallExecutionCampaign


def aggregate_telemetry(*, organisation=None, window_seconds: int = 3600) -> OperationalTelemetrySnapshot:
    since = timezone.now() - timedelta(seconds=window_seconds)
    scan_qs = ScanEvent.objects.filter(created_at__gte=since)
    event_qs = EventLifecycleLog.objects.filter(created_at__gte=since)
    if organisation:
        scan_qs = scan_qs.filter(organisation=organisation)
        event_qs = event_qs.filter(organisation=organisation)

    scan_count = scan_qs.count()
    event_count = event_qs.count()
    suspicious = scan_qs.filter(outcome_label__icontains="suspicious").count()
    verification_rate = Decimal(scan_count) if scan_count else Decimal(0)
    suspicious_rate = Decimal(suspicious * 100 / scan_count) if scan_count else Decimal(0)

    onboarding_qs = OrganisationOnboarding.objects.filter(submitted_at__gte=since)
    if organisation:
        onboarding_qs = onboarding_qs.filter(organisation=organisation)
    onboarding_velocity = onboarding_qs.count()

    campaigns = RecallExecutionCampaign.objects.filter(created_at__gte=since)
    recall_pct = Decimal(0)
    if campaigns.exists():
        c = campaigns.first()
        if c.pharmacies_targeted:
            recall_pct = Decimal(c.pharmacies_acknowledged * 100 / c.pharmacies_targeted)

    snap = OperationalTelemetrySnapshot.objects.create(
        organisation=organisation,
        window_seconds=window_seconds,
        scan_throughput=scan_count,
        event_throughput=event_count,
        verification_rate=verification_rate,
        suspicious_rate=suspicious_rate,
        onboarding_velocity=onboarding_velocity,
        recall_execution_pct=recall_pct,
        metrics={
            "scan_throughput": scan_count,
            "event_throughput": event_count,
            "suspicious_count": suspicious,
        },
    )
    publish_operational_event(
        event_type=EVT_TELEMETRY,
        payload={"snapshot_id": str(snap.id), "metrics": snap.metrics},
        organisation_id=organisation.id if organisation else None,
    )
    return snap
