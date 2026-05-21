"""Phase 12 — advanced counterfeit detection engine (deterministic, AI-ready)."""
from __future__ import annotations

from collections import defaultdict
from datetime import timedelta

from django.db.models import Count
from django.utils import timezone

from apps.organisations.models import Organisation
from apps.scanning.models import ScanEvent


def _severity(score: float) -> str:
    if score >= 80:
        return "critical"
    if score >= 60:
        return "high"
    if score >= 35:
        return "medium"
    return "low"


def analyze_counterfeit_national(*, window_hours: int = 168) -> dict:
    """National counterfeit analysis with confidence and escalation guidance."""
    since = timezone.now() - timedelta(hours=window_hours)
    scans = ScanEvent.objects.filter(created_at__gte=since).order_by("-created_at")
    total = max(scans.count(), 1)

    duplicate_serials = list(
        scans.values("serial_number")
        .annotate(c=Count("id"))
        .filter(c__gt=1)
        .order_by("-c")[:20]
    )

    impossible_travel = 0
    by_serial: dict[str, list] = defaultdict(list)
    for s in scans.only("serial_number", "latitude", "longitude", "created_at", "organisation_id")[:500]:
        if s.latitude and s.longitude:
            by_serial[s.serial_number].append(s)

    for serial, events in by_serial.items():
        if len(events) < 2:
            continue
        events.sort(key=lambda e: e.created_at)
        for i in range(1, len(events)):
            prev, curr = events[i - 1], events[i]
            dt_h = (curr.created_at - prev.created_at).total_seconds() / 3600
            if dt_h < 2 and prev.organisation_id != curr.organisation_id:
                impossible_travel += 1

    suspicious = scans.filter(outcome_label__icontains="suspicious").count()
    confidence = min(98, int(40 + (suspicious / total) * 50 + len(duplicate_serials) * 2))

    pharmacy_scores = []
    for org in Organisation.objects.filter(scan_events__created_at__gte=since).distinct()[:15]:
        org_scans = scans.filter(organisation=org)
        sus = org_scans.filter(outcome_label__icontains="suspicious").count()
        if org_scans.count() == 0:
            continue
        rate = sus / org_scans.count()
        if rate > 0.15:
            pharmacy_scores.append(
                {
                    "organisation_id": str(org.id),
                    "name": org.name,
                    "high_risk_score": int(rate * 100),
                }
            )

    regions = defaultdict(int)
    for s in scans.filter(outcome_label__icontains="suspicious").select_related("organisation")[:200]:
        state = s.organisation.state if s.organisation else "Unknown"
        regions[state] += 1

    heat_score = min(100, int(30 + suspicious * 2 + impossible_travel * 5))
    return {
        "confidence_score": confidence,
        "severity_classification": _severity(heat_score),
        "likely_counterfeit_source": "Diversion via unregistered wholesalers"
        if impossible_travel > 2
        else "Retail scan anomalies",
        "escalation_recommendation": "Activate regional enforcement sweep and border holds"
        if heat_score >= 70
        else "Increase pharmacy inspection sampling",
        "affected_regions": sorted(regions.keys(), key=lambda k: regions[k], reverse=True)[:8],
        "duplicate_serial_detection": duplicate_serials,
        "impossible_travel_events": impossible_travel,
        "suspicious_scan_cluster_count": suspicious,
        "high_risk_pharmacies": sorted(pharmacy_scores, key=lambda x: x["high_risk_score"], reverse=True)[:10],
        "fake_batch_pattern_indicators": len(duplicate_serials),
        "hotspot_analysis": dict(regions),
        "computed_at": timezone.now().isoformat(),
        "disclaimer": "Deterministic analysis — human review required before enforcement.",
    }
