"""Phase 12 — national pharmacy network intelligence."""
from __future__ import annotations

from apps.pharmacies.models import PharmacyProfile
from apps.scanning.models import ScanEvent


def pharmacy_network_ranking(*, limit: int = 30) -> list[dict]:
    profiles = PharmacyProfile.objects.select_related("organisation").all()[:limit]
    rows = []
    for p in profiles:
        org = p.organisation
        scans = ScanEvent.objects.filter(organisation=org).count()
        suspicious = ScanEvent.objects.filter(organisation=org, outcome_label__icontains="suspicious").count()
        dispense_anomaly = ScanEvent.objects.filter(
            organisation=org, scan_type=ScanEvent.SCAN_PHARMACY_DISPENSE, outcome_label__icontains="suspicious"
        ).count()
        score = 90
        if suspicious:
            score -= min(40, suspicious * 5)
        if not p.is_national_registry_verified:
            score -= 15
        rows.append(
            {
                "organisation_id": str(org.id),
                "name": org.name,
                "state": org.state,
                "operational_score": max(30, score),
                "inspection_history_count": 0,
                "violation_count": suspicious,
                "pharmacist_verified": bool(p.pharmacy_license_number),
                "dispensing_anomalies": dispense_anomaly,
                "suspicious_dispensing_pattern": dispense_anomaly > 1,
                "trusted_for_citizens": p.is_national_registry_verified and score >= 75,
                "compliance_badge": "verified" if score >= 80 else "monitoring" if score >= 60 else "review",
                "scan_volume": scans,
            }
        )
    return sorted(rows, key=lambda x: x["operational_score"], reverse=True)


def nearest_verified_pharmacies(*, state: str = "", limit: int = 10) -> list[dict]:
    qs = PharmacyProfile.objects.filter(is_national_registry_verified=True).select_related("organisation")
    if state:
        qs = qs.filter(organisation__state__iexact=state)
    return [
        {
            "name": p.organisation.name,
            "state": p.organisation.state,
            "license": p.pharmacy_license_number,
            "compliance_badge": "verified",
        }
        for p in qs[:limit]
    ]
