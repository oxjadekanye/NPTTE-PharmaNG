"""Phase 20C — national geospatial marker hydration from operational data."""
from __future__ import annotations

from typing import Any

from django.db.models import Q

from apps.command_orchestration.constants import MAP_LAYERS
from apps.enforcement.models import EnforcementCase
from apps.operations.models import OperationalTask
from apps.organisations.models import Organisation
from apps.scanning.models import ScanEvent

SUSPICIOUS_OUTCOMES = ("suspicious", "counterfeit", "invalid", "duplicate", "blacklisted")


def _float(v) -> float | None:
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _marker(
    *,
    marker_id: str,
    lat: float,
    lng: float,
    layer: str,
    organisation: str,
    severity: str,
    status: str,
    risk_score: int,
    active_incidents: int = 0,
    assigned_officer: str = "",
    explorer_entity_type: str = "",
    explorer_entity_id: str = "",
    title: str = "",
) -> dict[str, Any]:
    return {
        "id": marker_id,
        "lat": lat,
        "lng": lng,
        "layer": layer,
        "organisation": organisation,
        "severity": severity,
        "status": status,
        "risk_score": risk_score,
        "active_incidents": active_incidents,
        "assigned_officer": assigned_officer,
        "explorer_entity_type": explorer_entity_type,
        "explorer_entity_id": explorer_entity_id,
        "title": title,
    }


def _org_coords(org: Organisation) -> tuple[float, float] | None:
    lat = _float(org.latitude)
    lng = _float(org.longitude)
    if lat is None or lng is None:
        return None
    return lat, lng


def _markers_operational(limit: int) -> list[dict]:
    out: list[dict] = []
    for org in Organisation.objects.filter(latitude__isnull=False, longitude__isnull=False).order_by(
        "-updated_at"
    )[:limit]:
        coords = _org_coords(org)
        if not coords:
            continue
        lat, lng = coords
        open_tasks = OperationalTask.objects.filter(
            organisation_id=org.id, task_status__in=(OperationalTask.STATUS_OPEN, OperationalTask.STATUS_IN_PROGRESS)
        ).count()
        out.append(
            _marker(
                marker_id=f"org-{org.id}",
                lat=lat,
                lng=lng,
                layer="operational",
                organisation=org.legal_name,
                severity="medium" if open_tasks else "low",
                status="active",
                risk_score=min(40 + open_tasks * 8, 95),
                active_incidents=open_tasks,
                explorer_entity_type="organisation",
                explorer_entity_id=str(org.id),
                title=org.legal_name,
            )
        )
    return out


def _markers_counterfeit(limit: int) -> list[dict]:
    out: list[dict] = []
    qs = (
        ScanEvent.objects.select_related("organisation")
        .filter(
            Q(outcome_label__in=SUSPICIOUS_OUTCOMES)
            | Q(latitude__isnull=False)
        )
        .order_by("-created_at")[:limit]
    )
    for scan in qs:
        lat = _float(scan.latitude)
        lng = _float(scan.longitude)
        if (lat is None or lng is None) and scan.organisation_id:
            coords = _org_coords(scan.organisation)
            if coords:
                lat, lng = coords
        if lat is None or lng is None:
            continue
        sev = "critical" if scan.outcome_label in ("counterfeit", "blacklisted") else "high"
        out.append(
            _marker(
                marker_id=f"scan-{scan.id}",
                lat=lat,
                lng=lng,
                layer="counterfeit",
                organisation=scan.organisation.legal_name if scan.organisation else "Unknown site",
                severity=sev,
                status=scan.outcome_label or "suspicious",
                risk_score=85 if sev == "critical" else 70,
                active_incidents=1,
                explorer_entity_type="scan_event",
                explorer_entity_id=str(scan.id),
                title=f"Scan {scan.serial_number}",
            )
        )
    return out


def _markers_investigations(limit: int) -> list[dict]:
    out: list[dict] = []
    qs = EnforcementCase.objects.select_related("organisation", "assigned_regulator").exclude(
        case_status__in=(EnforcementCase.STATUS_RESOLVED, EnforcementCase.STATUS_CLOSED)
    )[:limit]
    for case in qs:
        lat = lng = None
        org_name = "National desk"
        if case.organisation_id:
            coords = _org_coords(case.organisation)
            if coords:
                lat, lng = coords
            org_name = case.organisation.legal_name
        if lat is None:
            lat, lng = 9.0579, 7.4951
        officer = ""
        if case.assigned_regulator_id:
            officer = case.assigned_regulator.get_full_name() or case.assigned_regulator.username
        out.append(
            _marker(
                marker_id=f"case-{case.id}",
                lat=lat,
                lng=lng,
                layer="investigations",
                organisation=org_name,
                severity=case.severity,
                status=case.case_status,
                risk_score=90 if case.severity == EnforcementCase.SEV_CRITICAL else 75,
                active_incidents=1,
                assigned_officer=officer,
                explorer_entity_type="enforcement_case",
                explorer_entity_id=str(case.id),
                title=case.title,
            )
        )
    return out


def _markers_enforcement(limit: int) -> list[dict]:
    return [m for m in _markers_investigations(limit) if m["status"] in ("escalated", "enforcement_pending")]


def _markers_customs(limit: int) -> list[dict]:
    out: list[dict] = []
    qs = ScanEvent.objects.select_related("organisation").filter(scan_type=ScanEvent.SCAN_CUSTOMS).order_by(
        "-created_at"
    )[:limit]
    for scan in qs:
        lat = _float(scan.latitude)
        lng = _float(scan.longitude)
        if (lat is None or lng is None) and scan.organisation_id:
            coords = _org_coords(scan.organisation)
            if coords:
                lat, lng = coords
        if lat is None or lng is None:
            lat, lng = 6.45, 3.35
        out.append(
            _marker(
                marker_id=f"customs-{scan.id}",
                lat=lat,
                lng=lng,
                layer="customs",
                organisation=scan.organisation.legal_name if scan.organisation else "Border post",
                severity="high",
                status=scan.outcome_label or "hold",
                risk_score=72,
                explorer_entity_type="scan_event",
                explorer_entity_id=str(scan.id),
                title="Customs incident",
            )
        )
    return out


def _markers_shortage(limit: int) -> list[dict]:
    from apps.alerts.models import NationalAlert

    out: list[dict] = []
    qs = NationalAlert.objects.filter(alert_type__icontains="shortage").order_by("-created_at")[:limit]
    for alert in qs:
        evidence = alert.evidence_payload if isinstance(alert.evidence_payload, dict) else {}
        lat = _float(evidence.get("latitude"))
        lng = _float(evidence.get("longitude"))
        state = evidence.get("state") or alert.title
        if lat is None or lng is None:
            lat, lng = 9.082, 8.6753
        out.append(
            _marker(
                marker_id=f"shortage-{alert.id}",
                lat=lat,
                lng=lng,
                layer="shortage",
                organisation=str(state),
                severity=alert.severity or "high",
                status="open" if not alert.resolved_at else "resolved",
                risk_score=78,
                explorer_entity_type="national_alert",
                explorer_entity_id=str(alert.id),
                title=alert.title,
            )
        )
    return out


def _markers_recalls(limit: int) -> list[dict]:
    from apps.alerts.models import NationalAlert

    out: list[dict] = []
    qs = NationalAlert.objects.filter(alert_type__icontains="recall").order_by("-created_at")[:limit]
    for alert in qs:
        evidence = alert.evidence_payload if isinstance(alert.evidence_payload, dict) else {}
        lat = _float(evidence.get("latitude"))
        lng = _float(evidence.get("longitude"))
        if lat is None or lng is None:
            lat, lng = 6.5244, 3.3792
        out.append(
            _marker(
                marker_id=f"recall-{alert.id}",
                lat=lat,
                lng=lng,
                layer="recalls",
                organisation=evidence.get("organisation") or "National recall desk",
                severity=alert.severity or "critical",
                status="active" if not alert.resolved_at else "resolved",
                risk_score=88,
                explorer_entity_type="national_alert",
                explorer_entity_id=str(alert.id),
                title=alert.title,
            )
        )
    return out


_LAYER_BUILDERS = {
    "operational": _markers_operational,
    "counterfeit": _markers_counterfeit,
    "recalls": _markers_recalls,
    "shortage": _markers_shortage,
    "investigations": _markers_investigations,
    "enforcement": _markers_enforcement,
    "customs": _markers_customs,
}


def build_map_markers(*, layer: str = "operational", limit: int = 120) -> dict:
    key = layer if layer in MAP_LAYERS else "operational"
    fn = _LAYER_BUILDERS.get(key, _markers_operational)
    markers = fn(limit)
    return {"layer": key, "markers": markers, "count": len(markers)}


def cluster_markers(markers: list[dict], *, cell_deg: float = 0.35) -> list[dict]:
    """Lightweight grid clustering for map performance."""
    buckets: dict[tuple[int, int], list[dict]] = {}
    for m in markers:
        lat, lng = m["lat"], m["lng"]
        key = (int(lat / cell_deg), int(lng / cell_deg))
        buckets.setdefault(key, []).append(m)

    clusters: list[dict] = []
    for idx, group in enumerate(buckets.values()):
        if len(group) == 1:
            clusters.append({**group[0], "cluster": False, "count": 1})
            continue
        lat = sum(g["lat"] for g in group) / len(group)
        lng = sum(g["lng"] for g in group) / len(group)
        max_risk = max(g["risk_score"] for g in group)
        clusters.append(
            {
                "id": f"cluster-{idx}",
                "lat": lat,
                "lng": lng,
                "layer": group[0]["layer"],
                "organisation": f"{len(group)} sites",
                "severity": group[0]["severity"],
                "status": "cluster",
                "risk_score": max_risk,
                "active_incidents": sum(g.get("active_incidents", 0) for g in group),
                "assigned_officer": "",
                "cluster": True,
                "count": len(group),
                "members": [{"id": g["id"], "title": g.get("title", "")} for g in group[:8]],
            }
        )
    return clusters
