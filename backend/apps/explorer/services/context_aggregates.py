"""Phase 20A.2 — rich context-specific explorer aggregates (unique per dashboard card)."""
from __future__ import annotations

from collections import Counter
from typing import Any, Callable

from django.db.models import Q
from django.utils import timezone

from apps.alerts.models import NationalAlert
from apps.enforcement.models import EnforcementCase, EnforcementRecommendation
from apps.intelligence.models import CounterfeitCluster, IntelligenceSignal, NationalRiskSnapshot
from apps.operational_demo.constants import DEMO_TYPE
from apps.products.models import Product
from apps.scanning.models import ScanEvent
from apps.serialization.models import ProductSerial

# Context key (normalized) -> aggregate entity_id for national_risk explorer routing
CONTEXT_TO_AGGREGATE: dict[str, str] = {
    "live_national_threat_composite": "live-national-threat-composite",
    "live-national-threat-composite": "live-national-threat-composite",
    "national_threat": "live-national-threat-composite",
    "api_health": "api-health-current",
    "api_health_current": "api-health-current",
    "national_ai": "national-ai-intelligence-current",
    "national_ai_intelligence": "national-ai-intelligence-current",
    "medicine_stability": "medicine-stability-current",
    "counterfeit_risk_forecast": "counterfeit-risk-forecast-current",
    "shortage_pressure": "shortage-pressure-current",
    "import_disruption": "import-disruption-current",
    "enforcement_readiness": "enforcement-readiness-current",
    "national_verifications": "national-verifications-current",
    "compliance_rate": "compliance-rate-current",
    "scan_success_rate": "scan-success-rate-current",
    "counterfeit_reduction": "counterfeit-reduction-current",
    "public_health_risk": "public-health-risk-current",
    "urgent_actions": "urgent-actions-current",
    "verifications": "national-verifications-current",
    "verifications_24h": "national-verifications-current",
    "national_verifications": "national-verifications-current",
    "compliance_rate": "compliance-rate-current",
    "scan_success_rate": "scan-success-rate-current",
    "counterfeit_reduction": "counterfeit-reduction-current",
    "counterfeit_detections": "counterfeit-detections-current",
    "open_alerts": "open-alerts-current",
    "fraud_flags": "fraud-flags-current",
    "active_investigations": "active-investigations-current",
    "products_tracked": "products-tracked-current",
    "recalls": "recalls-current",
    "emergency_recalls": "emergency-recalls-current",
    "blacklisted_batches": "blacklisted-batches-current",
    "cold_chain_breaches": "cold-chain-breaches-current",
    "customs_holds": "customs-holds-current",
    "invalid_serials": "invalid-serials-current",
    "duplicate_serials": "duplicate-serials-current",
    "recall_non_acknowledgements": "recall-non-acknowledgements-current",
    "shortage_alerts": "shortage-alerts-current",
    "public_reports": "public-reports-current",
    "national_status": "live-national-threat-composite",
    "national_risk": "national-risk-current",
}


def aggregate_id_for_context(context_key: str) -> str:
    key = (context_key or "").strip().lower().replace("-", "_")
    return CONTEXT_TO_AGGREGATE.get(key, "national-risk-current")


def _demo_alert_qs(**filters):
    q = Q(metadata__demo_type=DEMO_TYPE) | Q(evidence_payload__demo_type=DEMO_TYPE)
    return NationalAlert.objects.filter(q, **filters)


def _demo_signal_qs(**filters):
    q = Q(metadata__demo_type=DEMO_TYPE) | Q(evidence__demo_type=DEMO_TYPE)
    return IntelligenceSignal.objects.filter(q, **filters)


def _record_from_alert(a: NationalAlert) -> dict[str, Any]:
    ev = a.evidence_payload if isinstance(a.evidence_payload, dict) else {}
    org = a.organisation
    return {
        "id": str(a.id),
        "entity_type": "alert",
        "title": a.title,
        "severity": a.severity,
        "status": "resolved" if a.resolved_at else ev.get("action_status", "open"),
        "organisation": org.legal_name if org else ev.get("organisation_name", ""),
        "organisation_type": org.organisation_type.code if org else ev.get("organisation_type", ""),
        "address": org.address_line_1 if org else ev.get("address", ""),
        "state": a.state or ev.get("state", ""),
        "city": ev.get("city", org.city if org else ""),
        "phone": org.phone_number if org else ev.get("phone", ""),
        "contact_person": ev.get("contact_person", ""),
        "product": ev.get("product", a.product.name if a.product_id else ""),
        "batch": ev.get("batch", ""),
        "serial": ev.get("serial", ""),
        "detected_at": ev.get("detected_at", a.created_at.isoformat()),
        "detection_source": ev.get("detection_source", a.alert_type),
        "risk_score": float(a.risk_score),
        "confidence_score": ev.get("confidence_score"),
        "recommended_action": ev.get("recommended_action", ""),
        "assigned_officer": ev.get("assigned_officer", ""),
        "action_status": ev.get("action_status", "open"),
        "escalation_status": ev.get("escalation_status", "none"),
        "linked_case": ev.get("linked_case", ""),
    }


def _record_from_scan(s: ScanEvent) -> dict[str, Any]:
    rp = s.result_payload if isinstance(s.result_payload, dict) else {}
    org = s.organisation
    return {
        "id": str(s.id),
        "entity_type": "scan_event",
        "title": f"Scan {s.serial_number[:24]}",
        "severity": "critical" if s.outcome_label in ("invalid", "suspicious", "duplicate") else "medium",
        "status": s.outcome_label or s.scan_type,
        "organisation": org.legal_name if org else "",
        "organisation_type": org.organisation_type.code if org else "",
        "address": org.address_line_1 if org else "",
        "state": rp.get("state", org.state if org else ""),
        "city": rp.get("city", org.city if org else ""),
        "phone": org.phone_number if org else "",
        "serial": s.serial_number,
        "detected_at": s.created_at.isoformat(),
        "detection_source": s.scan_type,
        "risk_score": float(s.risk_score),
        "recommended_action": "Verify custody chain",
        "action_status": "open",
    }


def _severity_distribution(records: list[dict]) -> dict[str, int]:
    return dict(Counter(r.get("severity", "unknown") for r in records))


def _state_distribution(records: list[dict]) -> dict[str, int]:
    return dict(Counter(r.get("state", "unknown") for r in records if r.get("state")))


def build_context_aggregate_bundle(
    *, aggregate_id: str, request=None, record_limit: int = 100
) -> dict[str, Any]:
    """Build a full explorer-style bundle for a context aggregate pseudo-ID."""
    now = timezone.now().isoformat()
    base: dict[str, Any] = {
        "_record_limit": record_limit,
        "entity_type": "national_risk",
        "entity_id": aggregate_id,
        "last_updated": now,
        "tenant_visibility": "regulator_national",
        "aggregate": True,
        "context_key": aggregate_id,
        "summary": {"title": aggregate_id.replace("-", " ").title(), "aggregate": True},
        "records": [],
        "related_entities": {"nodes": [], "edges": []},
        "timeline": [],
        "evidence": [],
        "risk_explanation": {},
        "recommended_actions": [],
        "severity_distribution": {},
        "state_distribution": {},
        "record_count": 0,
    }

    builders: dict[str, Callable[[], None]] = {
        "counterfeit-detections-current": lambda: _fill_alerts(
            base, _demo_alert_qs(alert_type__icontains="counterfeit") | _demo_alert_qs(alert_type="counterfeit_detection"),
            title="Counterfeit detections",
            body="National counterfeit and cluster intelligence",
        ),
        "invalid-serials-current": lambda: _fill_alerts(
            base, _demo_alert_qs(alert_type="invalid_serial"),
            title="Invalid serial events",
            body="Serial numbers failing national verification",
        ),
        "suspicious-scans-current": lambda: _fill_scans(
            base, ScanEvent.objects.filter(metadata__demo_type=DEMO_TYPE, outcome_label="suspicious"),
            title="Suspicious scans",
        ),
        "open-alerts-current": lambda: _fill_alerts(
            base, _demo_alert_qs(resolved_at__isnull=True),
            title="Open national alerts",
            body="Unresolved regulator alerts requiring action",
        ),
        "fraud-flags-current": lambda: _fill_alerts(
            base, _demo_alert_qs(alert_type__icontains="fraud") | _demo_alert_qs(alert_type="blacklisted_batch"),
            title="Fraud and blacklist flags",
        ),
        "active-investigations-current": lambda: _fill_cases(base),
        "national-verifications-current": lambda: _fill_scans(
            base,
            ScanEvent.objects.filter(metadata__demo_type=DEMO_TYPE).order_by("-created_at")[:200],
            title="National verifications (24h roll)",
        ),
        "compliance-rate-current": lambda: _fill_compliance(base),
        "scan-success-rate-current": lambda: _fill_scan_success(base),
        "counterfeit-risk-forecast-current": lambda: _fill_forecast(base),
        "medicine-stability-current": lambda: _fill_stability(base),
        "shortage-pressure-current": lambda: _fill_alerts(
            base, _demo_alert_qs(alert_type__icontains="shortage"),
            title="Shortage pressure",
        ),
        "import-disruption-current": lambda: _fill_alerts(
            base, _demo_alert_qs(alert_type__icontains="customs"),
            title="Import disruption indicators",
        ),
        "enforcement-readiness-current": lambda: _fill_enforcement_readiness(base),
        "api-health-current": lambda: _fill_api_health(base),
        "national-ai-intelligence-current": lambda: _fill_ai_intel(base),
        "live-national-threat-composite": lambda: _fill_national_composite(base),
        "national-risk-current": lambda: _fill_national_composite(base),
        "products-tracked-current": lambda: _fill_products(base),
        "emergency-recalls-current": lambda: _fill_alerts(
            base, _demo_alert_qs(alert_type__icontains="recall"),
            title="Emergency recalls",
        ),
        "blacklisted-batches-current": lambda: _fill_alerts(
            base, _demo_alert_qs(alert_type="blacklisted_batch"),
            title="Blacklisted batches",
        ),
        "cold-chain-breaches-current": lambda: _fill_alerts(
            base, _demo_alert_qs(alert_type="cold_chain_breach"),
            title="Cold-chain breaches",
        ),
        "customs-holds-current": lambda: _fill_alerts(
            base, _demo_alert_qs(alert_type="customs_hold"),
            title="Customs holds",
        ),
        "duplicate-serials-current": lambda: _fill_alerts(
            base, _demo_alert_qs(alert_type="duplicate_serial"),
            title="Duplicate serial detections",
        ),
        "recall-non-acknowledgements-current": lambda: _fill_alerts(
            base, _demo_alert_qs(alert_type="recall_non_ack"),
            title="Recall non-acknowledgements",
        ),
        "shortage-alerts-current": lambda: _fill_alerts(
            base, _demo_alert_qs(alert_type="shortage_alert"),
            title="Medicine shortage alerts",
        ),
        "public-reports-current": lambda: _fill_alerts(
            base, _demo_alert_qs(alert_type="citizen_report"),
            title="Public citizen reports",
        ),
        "urgent-actions-current": lambda: _fill_urgent(base),
        "public-health-risk-current": lambda: _fill_public_health(base),
        "counterfeit-reduction-current": lambda: _fill_counterfeit_reduction(base),
    }

    fn = builders.get(aggregate_id, builders.get("national-risk-current"))
    if fn:
        fn()
    else:
        _fill_national_composite(base)

    records = base.get("records") or []
    if isinstance(records, list) and len(records) > record_limit:
        base["records"] = records[:record_limit]
        records = base["records"]
    if isinstance(records, dict) and "items" in records:
        items = records["items"]
    else:
        items = records if isinstance(records, list) else []
    base["record_count"] = len(items)
    base["severity_distribution"] = _severity_distribution(items)
    base["state_distribution"] = _state_distribution(items)
    return base


def _record_limit(base: dict, default: int = 100) -> int:
    try:
        return int(base.get("_record_limit") or default)
    except (TypeError, ValueError):
        return default


def _fill_alerts(base: dict, qs, *, title: str, body: str = "") -> None:
    limit = _record_limit(base, 100)
    rows = list(
        qs.select_related("organisation", "organisation__organisation_type", "product").order_by(
            "-created_at"
        )[:limit]
    )
    base["summary"] = {
        "title": title,
        "body": body or f"{len(rows)} operational records in national demo dataset",
        "count": len(rows),
        "severity": "critical" if any(r.severity == "critical" for r in rows[:20]) else "warning",
    }
    base["records"] = [_record_from_alert(a) for a in rows]
    base["recommended_actions"] = [
        "Assign field inspector to top-risk sites",
        "Open enforcement case for critical clusters",
        "Issue regional pharmacy advisory",
    ]


def _fill_scans(base: dict, qs, *, title: str) -> None:
    limit = _record_limit(base, 100)
    rows = list(
        qs.select_related("organisation", "organisation__organisation_type").order_by("-created_at")[:limit]
    )
    base["summary"] = {"title": title, "count": len(rows), "body": f"{len(rows)} verification events"}
    base["records"] = [_record_from_scan(s) for s in rows]


def _fill_cases(base: dict) -> None:
    qs = (
        EnforcementCase.objects.exclude(case_status="closed")
        .select_related("organisation", "assigned_regulator")
        .order_by("-created_at")[:80]
    )
    base["summary"] = {"title": "Active investigations", "count": qs.count()}
    base["records"] = [
        {
            "id": str(c.id),
            "entity_type": "enforcement_case",
            "title": c.title,
            "severity": c.severity,
            "status": c.case_status,
            "reference": c.case_reference,
            "organisation": c.organisation.legal_name if c.organisation_id else "",
            "assigned_officer": c.assigned_regulator.get_full_name() if c.assigned_regulator_id else "",
            "recommended_action": "Continue investigation",
            "detected_at": c.created_at.isoformat(),
        }
        for c in qs
    ]


def _fill_products(base: dict) -> None:
    qs = Product.objects.filter(metadata__demo_type=DEMO_TYPE).order_by("-created_at")[:120]
    if not qs.exists():
        qs = Product.objects.order_by("-created_at")[:120]
    base["summary"] = {"title": "Products tracked nationally", "count": qs.count()}
    base["records"] = [
        {
            "id": str(p.id),
            "entity_type": "product",
            "title": p.name,
            "status": "active",
            "product": p.name,
            "organisation": p.manufacturer.legal_name if p.manufacturer_id else "",
        }
        for p in qs
    ]


def _fill_national_composite(base: dict) -> None:
    snap = NationalRiskSnapshot.objects.order_by("-created_at").first()
    open_alerts = _demo_alert_qs(resolved_at__isnull=True).count()
    signals = _demo_signal_qs(is_active=True).count()
    base["summary"] = {
        "title": "Live national threat composite",
        "score": float(snap.national_score) if snap else 62.0,
        "status": snap.status if snap else "amber",
        "body": f"{open_alerts} open alerts · {signals} active signals",
        "count": open_alerts + signals,
    }
    base["risk_explanation"] = {"reasons": (snap.reasons if snap else [])[:6]}
    base["recommended_actions"] = (snap.recommended_actions if snap else [])[:5]
    rec = list(_demo_alert_qs(resolved_at__isnull=True).order_by("-risk_score")[:15])
    base["records"] = [_record_from_alert(a) for a in rec]


def _fill_compliance(base: dict) -> None:
    total = ScanEvent.objects.filter(metadata__demo_type=DEMO_TYPE).count() or 1
    ok = ScanEvent.objects.filter(metadata__demo_type=DEMO_TYPE, outcome_label="authentic").count()
    rate = round(100.0 * ok / total, 1)
    base["summary"] = {"title": "National compliance rate", "score": rate, "body": f"{ok}/{total} authentic scans"}
    base["records"] = []


def _fill_scan_success(base: dict) -> None:
    total = ProductSerial.objects.filter(metadata__demo_type=DEMO_TYPE).count() or 1
    disp = ProductSerial.objects.filter(metadata__demo_type=DEMO_TYPE, is_dispensed=True).count()
    rate = round(100.0 * disp / total, 1)
    base["summary"] = {"title": "Scan success / dispense rate", "score": rate}


def _fill_forecast(base: dict) -> None:
    clusters = CounterfeitCluster.objects.filter(status="open").order_by("-suspicious_count")[:12]
    base["summary"] = {
        "title": "Counterfeit risk forecast",
        "body": "High-risk products and states from open clusters",
        "count": clusters.count(),
    }
    base["records"] = [
        {
            "id": str(c.id),
            "entity_type": "counterfeit_cluster",
            "title": c.cluster_code,
            "severity": "critical",
            "state": c.region_state,
            "product": c.product.name if c.product_id else "",
            "status": c.status,
            "risk_score": float(c.confidence),
        }
        for c in clusters
    ]


def _fill_stability(base: dict) -> None:
    shortage = _demo_alert_qs(alert_type__icontains="shortage").count()
    recall = _demo_alert_qs(alert_type__icontains="recall").count()
    base["summary"] = {
        "title": "Medicine stability index",
        "score": max(0, 100 - shortage * 2 - recall),
        "body": f"{shortage} shortage signals · {recall} recall-related alerts",
    }
    base["records"] = [_record_from_alert(a) for a in _demo_alert_qs(alert_type__icontains="shortage")[:40]]


def _fill_enforcement_readiness(base: dict) -> None:
    pending = EnforcementRecommendation.objects.filter(
        recommendation_status=EnforcementRecommendation.STATUS_PENDING
    ).count()
    cases = EnforcementCase.objects.exclude(case_status="closed").count()
    base["summary"] = {
        "title": "Enforcement readiness",
        "count": pending + cases,
        "body": f"{pending} pending recommendations · {cases} open cases",
    }
    base["records"] = [
        {
            "id": str(r.id),
            "entity_type": "enforcement_recommendation",
            "title": r.title,
            "severity": r.severity,
            "status": r.recommendation_status,
            "recommended_action": r.recommendation_type,
        }
        for r in EnforcementRecommendation.objects.filter(
            recommendation_status=EnforcementRecommendation.STATUS_PENDING
        )[:30]
    ]


def _fill_api_health(base: dict) -> None:
    base["summary"] = {
        "title": "API & integration health",
        "status": "healthy",
        "body": "Core regulator APIs responding within SLA",
        "count": 6,
    }
    base["records"] = [
        {"title": "Explorer API", "status": "ok", "severity": "normal", "detection_source": "synthetic"},
        {"title": "Intelligence API", "status": "ok", "severity": "normal", "detection_source": "synthetic"},
        {"title": "Enforcement API", "status": "ok", "severity": "normal", "detection_source": "synthetic"},
        {"title": "Streambus SSE", "status": "ok", "severity": "normal", "detection_source": "synthetic"},
        {"title": "Verification scans", "status": "ok", "severity": "normal", "detection_source": "synthetic"},
        {"title": "Executive briefing", "status": "ok", "severity": "normal", "detection_source": "synthetic"},
    ]


def _fill_ai_intel(base: dict) -> None:
    sig = _demo_signal_qs(is_active=True).order_by("-confidence")[:25]
    base["summary"] = {
        "title": "National AI intelligence snapshot",
        "body": "Top confidence signals from national demo corpus",
        "count": sig.count(),
    }
    base["records"] = [
        {
            "id": str(s.id),
            "entity_type": "intelligence_signal",
            "title": s.title,
            "severity": s.severity,
            "state": s.region_state,
            "confidence_score": float(s.confidence),
            "detected_at": s.created_at.isoformat(),
        }
        for s in sig
    ]


def _fill_urgent(base: dict) -> None:
    crit = _demo_alert_qs(severity="critical", resolved_at__isnull=True).order_by("-risk_score")[:25]
    base["summary"] = {"title": "Urgent actions queue", "count": crit.count(), "severity": "critical"}
    base["records"] = [_record_from_alert(a) for a in crit]


def _fill_public_health(base: dict) -> None:
    keys = ["shortage", "recall", "cold_chain", "counterfeit"]
    q = Q()
    for k in keys:
        q |= Q(alert_type__icontains=k)
    rows = _demo_alert_qs(q).order_by("-created_at")[:60]
    base["summary"] = {"title": "Public health risk indicators", "count": rows.count()}
    base["records"] = [_record_from_alert(a) for a in rows]


def _fill_counterfeit_reduction(base: dict) -> None:
    base["summary"] = {
        "title": "Counterfeit reduction (YoY)",
        "score": 18.4,
        "body": "Demo trend: reduction driven by verification uptake in Lagos & Kano",
    }
    base["records"] = [_record_from_alert(a) for a in _demo_alert_qs(alert_type__icontains="counterfeit")[:20]]
