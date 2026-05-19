"""Assemble explorer payloads: detail, aggregates, graph, timeline, evidence."""
from __future__ import annotations

import uuid
from typing import Any

from django.utils import timezone

from apps.alerts.models import NationalAlert
from apps.command_center.models import NationalIncident
from apps.enforcement.models import EnforcementCase, EnforcementRecommendation, EnforcementTimelineEntry
from apps.explorer.constants import AGGREGATE_IDS
from apps.explorer.services import risk_breakdown
from apps.intelligence.models import CounterfeitCluster, IntelligenceSignal, NationalRiskSnapshot
from apps.intelligence.services.scoring import calculate_national_risk
from apps.notifications.models import Notification
from apps.operations.models import ActivityFeedEntry, OperationalDocument, OperationalTask, WorkflowTimelineEntry
from apps.organisations.models import Organisation
from apps.products.models import Product, ProductBatch
from apps.scanning.models import ScanEvent
from apps.traceability.models import BatchRecall


def get_access_handles(entity_type: str, entity_id: str) -> dict[str, Any]:
    """Load minimal FK info for access_control (no payload)."""
    uid = _uuid_or_none(entity_id)
    handles: dict[str, Any] = {
        "organisation_id": None,
        "notification_recipient_id": None,
        "region_state": None,
        "missing": False,
        "invalid_uuid": False,
    }
    if entity_id in AGGREGATE_IDS:
        return handles

    if uid is None and entity_type != "regional_risk":
        handles["invalid_uuid"] = True
        return handles

    try:
        if entity_type == "organisation" and uid:
            handles["organisation_id"] = uid
        elif entity_type == "product" and uid:
            p = Product.objects.filter(pk=uid).values("manufacturer_id").first()
            if p and p.get("manufacturer_id"):
                handles["organisation_id"] = p["manufacturer_id"]
        elif entity_type == "scan_event" and uid:
            s = ScanEvent.objects.filter(pk=uid).values("organisation_id").first()
            if s and s.get("organisation_id"):
                handles["organisation_id"] = s["organisation_id"]
        elif entity_type == "intelligence_signal" and uid:
            s = IntelligenceSignal.objects.filter(pk=uid).values("organisation_id").first()
            if s and s.get("organisation_id"):
                handles["organisation_id"] = s["organisation_id"]
        elif entity_type == "enforcement_case" and uid:
            c = EnforcementCase.objects.filter(pk=uid).values("organisation_id").first()
            if c and c.get("organisation_id"):
                handles["organisation_id"] = c["organisation_id"]
        elif entity_type == "enforcement_recommendation" and uid:
            r = EnforcementRecommendation.objects.filter(pk=uid).values("organisation_id").first()
            if r and r.get("organisation_id"):
                handles["organisation_id"] = r["organisation_id"]
        elif entity_type == "notification" and uid:
            n = Notification.objects.filter(pk=uid).values("recipient_id", "organisation_id").first()
            if not n:
                handles["missing"] = True
            else:
                handles["notification_recipient_id"] = n["recipient_id"]
                if n.get("organisation_id"):
                    handles["organisation_id"] = n["organisation_id"]
        elif entity_type == "incident" and uid:
            i = NationalIncident.objects.filter(pk=uid).values("organisation_id").first()
            if not i:
                handles["missing"] = True
            elif i.get("organisation_id"):
                handles["organisation_id"] = i["organisation_id"]
        elif entity_type == "alert" and uid:
            a = NationalAlert.objects.filter(pk=uid).values("organisation_id").first()
            if not a:
                handles["missing"] = True
            elif a.get("organisation_id"):
                handles["organisation_id"] = a["organisation_id"]
        elif entity_type == "task" and uid:
            t = OperationalTask.objects.filter(pk=uid).values("organisation_id").first()
            if not t:
                handles["missing"] = True
            elif t.get("organisation_id"):
                handles["organisation_id"] = t["organisation_id"]
        elif entity_type == "document" and uid:
            d = OperationalDocument.objects.filter(pk=uid).values("organisation_id").first()
            if not d:
                handles["missing"] = True
            else:
                handles["organisation_id"] = d["organisation_id"]
        elif entity_type == "recall" and uid:
            br = BatchRecall.objects.filter(pk=uid).select_related("batch__product").first()
            if not br:
                handles["missing"] = True
            elif br.batch and br.batch.product and br.batch.product.manufacturer_id:
                handles["organisation_id"] = br.batch.product.manufacturer_id
        elif entity_type == "batch" and uid:
            b = ProductBatch.objects.filter(pk=uid).select_related("product").first()
            if not b:
                handles["missing"] = True
            elif b.product and b.product.manufacturer_id:
                handles["organisation_id"] = b.product.manufacturer_id
        elif entity_type == "regional_risk":
            handles["region_state"] = entity_id
        elif entity_type == "counterfeit_cluster" and uid:
            c = CounterfeitCluster.objects.filter(pk=uid).values("product_id").first()
            if c and c.get("product_id"):
                mid = (
                    Product.objects.filter(pk=c["product_id"])
                    .values_list("manufacturer_id", flat=True)
                    .first()
                )
                if mid:
                    handles["organisation_id"] = mid
    except Exception:
        handles["missing"] = True
    return handles


def _uuid_or_none(s: str) -> uuid.UUID | None:
    try:
        return uuid.UUID(str(s))
    except (ValueError, TypeError):
        return None


def build_graph_stub(*, entity_type: str, entity_id: str, summary_row: dict | None) -> dict[str, Any]:
    nodes: list[dict] = []
    edges: list[dict] = []
    nid = f"{entity_type}:{entity_id}"
    nodes.append({"id": nid, "label": entity_type.replace("_", " ").title(), "kind": entity_type})
    if summary_row and summary_row.get("linked_product_id"):
        pid = str(summary_row["linked_product_id"])
        nodes.append({"id": f"product:{pid}", "label": "Product", "kind": "product"})
        edges.append({"source": nid, "target": f"product:{pid}", "relation": "linked_to"})
    if summary_row and summary_row.get("linked_organisation_id"):
        oid = str(summary_row["linked_organisation_id"])
        nodes.append({"id": f"organisation:{oid}", "label": "Organisation", "kind": "organisation"})
        edges.append({"source": nid, "target": f"organisation:{oid}", "relation": "linked_to"})
    return {"nodes": nodes, "edges": edges}


def build_timeline_entries(entity_type: str, entity_id: str, *, limit: int = 40) -> list[dict]:
    uid = _uuid_or_none(entity_id)
    out: list[dict] = []
    if entity_type == "enforcement_case" and uid:
        for e in EnforcementTimelineEntry.objects.filter(case_id=uid).order_by("-created_at")[:limit]:
            out.append(
                {
                    "id": str(e.id),
                    "entry_type": e.entry_type,
                    "summary": e.summary,
                    "created_at": e.created_at.isoformat(),
                }
            )
    elif uid and entity_type in ("organisation", "product", "batch"):
        org_id = None
        if entity_type == "organisation":
            org_id = uid
        elif entity_type == "product":
            org_id = (
                Product.objects.filter(pk=uid).values_list("manufacturer_id", flat=True).first()
            )
        elif entity_type == "batch":
            b = ProductBatch.objects.filter(pk=uid).select_related("product").first()
            if b and b.product:
                org_id = b.product.manufacturer_id
        if org_id:
            for w in WorkflowTimelineEntry.objects.filter(organisation_id=org_id).order_by("-created_at")[:limit]:
                out.append(
                    {
                        "id": str(w.id),
                        "entry_type": w.workflow_type,
                        "summary": w.title,
                        "created_at": w.created_at.isoformat(),
                    }
                )
    return out


def build_evidence_entries(entity_type: str, entity_id: str, *, limit: int = 30) -> list[dict]:
    uid = _uuid_or_none(entity_id)
    rows: list[dict] = []
    if entity_type == "intelligence_signal" and uid:
        s = IntelligenceSignal.objects.filter(pk=uid).first()
        if s and s.evidence:
            rows.append({"kind": "signal_evidence", "payload": s.evidence})
    elif entity_type == "alert" and uid:
        a = NationalAlert.objects.filter(pk=uid).first()
        if a and a.evidence_payload:
            rows.append({"kind": "alert_evidence", "payload": a.evidence_payload})
    elif entity_type == "scan_event" and uid:
        s = ScanEvent.objects.filter(pk=uid).first()
        if s:
            rows.append({"kind": "scan_payload", "payload": s.result_payload})
    return rows[:limit]


def build_recommended_actions(entity_type: str, bundle: dict) -> list[str]:
    ra = bundle.get("risk_explanation", {}).get("recommended_actions")
    if isinstance(ra, list):
        return ra
    return bundle.get("summary", {}).get("recommended_actions", []) or []


def build_explorer_bundle(request, entity_type: str, entity_id: str) -> dict[str, Any]:
    """Full explorer payload for detail drawer and detail pages."""
    now = timezone.now().isoformat()
    tenant_visibility = "regulator_national"
    user = request.user
    from apps.core.roles import is_regulator_user

    if not is_regulator_user(user) and not user.is_superuser:
        tenant_visibility = "organisation_scoped"

    base = {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "last_updated": now,
        "tenant_visibility": tenant_visibility,
        "source_systems": ["nptte_core", "intelligence", "enforcement", "operations", "scanning", "alerts"],
        "confidence_score": None,
        "summary": {},
        "records": [],
        "related_entities": {"nodes": [], "edges": []},
        "timeline": [],
        "evidence": [],
        "risk_explanation": {},
        "recommended_actions": [],
    }

    if entity_id in AGGREGATE_IDS:
        return _aggregate_bundle(request, entity_type, entity_id, base)

    uid = _uuid_or_none(entity_id)
    if uid is None and entity_type != "regional_risk":
        base["summary"] = {"error": "invalid_entity_id"}
        return base

    if entity_type == "national_risk" and uid:
        snap = NationalRiskSnapshot.objects.filter(pk=uid).first()
        if snap:
            base["summary"] = {
                "title": "National risk snapshot",
                "body": "; ".join(snap.reasons[:5]) if snap.reasons else "",
                "status": snap.status,
                "score": float(snap.national_score),
            }
            base["confidence_score"] = float(snap.confidence)
            base["risk_explanation"] = risk_breakdown.national_risk_breakdown()
            base["recommended_actions"] = snap.recommended_actions or []
        return base

    if entity_type == "regional_risk":
        rs = entity_id
        base["risk_explanation"] = risk_breakdown.regional_risk_breakdown(rs)
        base["summary"] = {
            "title": f"Regional risk — {rs}",
            "status": base["risk_explanation"].get("status"),
            "score": base["risk_explanation"].get("score"),
        }
        base["confidence_score"] = base["risk_explanation"].get("confidence")
        base["recommended_actions"] = base["risk_explanation"].get("recommended_actions", [])
        base["related_entities"] = build_graph_stub(
            entity_type=entity_type, entity_id=entity_id, summary_row={"linked_organisation_id": None}
        )
        return base

    if entity_type == "organisation" and uid:
        org = Organisation.objects.filter(pk=uid).first()
        if org:
            rb = risk_breakdown.organisation_risk_breakdown(org)
            base["summary"] = {"title": org.legal_name, "status": rb["status"], "score": rb["score"]}
            base["risk_explanation"] = rb
            base["recommended_actions"] = rb.get("recommended_actions", [])
            base["confidence_score"] = rb.get("confidence")
            base["related_entities"] = build_graph_stub(
                entity_type=entity_type,
                entity_id=entity_id,
                summary_row={"linked_organisation_id": str(org.id)},
            )
        return base

    if entity_type == "product" and uid:
        p = Product.objects.filter(pk=uid).select_related("manufacturer").first()
        if p:
            rb = risk_breakdown.product_risk_breakdown(p)
            base["summary"] = {"title": p.name, "status": rb["status"], "score": rb["score"]}
            base["risk_explanation"] = rb
            base["recommended_actions"] = rb.get("recommended_actions", [])
            base["confidence_score"] = rb.get("confidence")
            base["related_entities"] = build_graph_stub(
                entity_type=entity_type,
                entity_id=entity_id,
                summary_row={
                    "linked_product_id": str(p.id),
                    "linked_organisation_id": str(p.manufacturer_id) if p.manufacturer_id else None,
                },
            )
        return base

    if entity_type == "scan_event" and uid:
        s = ScanEvent.objects.filter(pk=uid).select_related("organisation").first()
        if s:
            base["summary"] = {
                "title": f"Scan {s.serial_number[:24]}…",
                "status": s.outcome_label or s.scan_type,
                "score": float(s.risk_score),
            }
            base["confidence_score"] = float(s.risk_score)
            base["evidence"] = build_evidence_entries(entity_type, entity_id)
            base["timeline"] = [{"entry_type": "scan", "summary": s.scan_type, "created_at": s.created_at.isoformat()}]
        return base

    if entity_type == "intelligence_signal" and uid:
        s = IntelligenceSignal.objects.filter(pk=uid).first()
        if s:
            base["summary"] = {
                "title": s.title,
                "severity": s.severity,
                "body": s.summary,
            }
            base["confidence_score"] = float(s.confidence)
            base["evidence"] = build_evidence_entries(entity_type, entity_id)
        return base

    if entity_type == "enforcement_case" and uid:
        c = EnforcementCase.objects.filter(pk=uid).first()
        if c:
            base["summary"] = {
                "title": c.title,
                "status": c.case_status,
                "severity": c.severity,
                "reference": c.case_reference,
            }
            base["timeline"] = build_timeline_entries(entity_type, entity_id)
        return base

    if entity_type == "enforcement_recommendation" and uid:
        r = EnforcementRecommendation.objects.filter(pk=uid).first()
        if r:
            base["summary"] = {
                "title": r.title,
                "status": r.recommendation_status,
                "severity": r.severity,
                "body": r.rationale,
            }
            base["confidence_score"] = float(r.risk_score)
        return base

    if entity_type == "notification" and uid:
        n = Notification.objects.filter(pk=uid).first()
        if n:
            base["summary"] = {
                "title": n.title,
                "severity": n.severity,
                "body": n.body,
                "is_read": n.is_read,
            }
            base["confidence_score"] = 80.0
        return base

    if entity_type == "incident" and uid:
        i = NationalIncident.objects.filter(pk=uid).first()
        if i:
            base["summary"] = {
                "title": i.title,
                "status": i.status,
                "severity": i.severity,
                "code": i.incident_code,
            }
            base["confidence_score"] = float(i.threat_score)
            base["related_entities"] = build_graph_stub(
                entity_type=entity_type,
                entity_id=entity_id,
                summary_row={
                    "linked_organisation_id": str(i.organisation_id) if i.organisation_id else None,
                    "linked_product_id": str(i.product_id) if i.product_id else None,
                },
            )
        return base

    if entity_type == "alert" and uid:
        a = NationalAlert.objects.filter(pk=uid).first()
        if a:
            base["summary"] = {"title": a.title, "severity": a.severity, "body": a.description}
            base["confidence_score"] = float(a.risk_score)
            base["evidence"] = build_evidence_entries(entity_type, entity_id)
        return base

    if entity_type == "task" and uid:
        t = OperationalTask.objects.filter(pk=uid).first()
        if t:
            base["summary"] = {
                "title": t.title,
                "status": t.task_status,
                "severity": t.priority,
                "body": t.description,
            }
        return base

        if entity_type == "document" and uid:
            d = OperationalDocument.objects.filter(pk=uid).first()
            if d:
                base["summary"] = {"title": d.title, "status": d.document_type, "body": d.original_filename or ""}
        return base

    if entity_type == "counterfeit_cluster" and uid:
        c = CounterfeitCluster.objects.filter(pk=uid).first()
        if c:
            base["summary"] = {
                "title": c.cluster_code,
                "status": c.status,
                "body": f"{c.suspicious_count} suspicious / {c.scan_count} scans",
            }
            base["confidence_score"] = float(c.confidence)
        return base

    if entity_type == "recall" and uid:
        br = BatchRecall.objects.filter(pk=uid).select_related("batch__product").first()
        if br:
            base["summary"] = {
                "title": f"Recall {br.id}",
                "status": "active",
                "body": (br.recall_reason or "")[:500],
            }
        return base

    if entity_type == "batch" and uid:
        b = ProductBatch.objects.filter(pk=uid).select_related("product").first()
        if b:
            base["summary"] = {
                "title": f"Batch {b.batch_number}",
                "status": getattr(b, "lifecycle_status", "") or "",
                "body": b.product.name if b.product else "",
            }
        return base

    base["summary"] = {"title": entity_type, "body": "Explorer stub — extend in later phases."}
    return base


def _aggregate_bundle(request, entity_type: str, entity_id: str, base: dict) -> dict:
    from apps.explorer.services.context_aggregates import build_context_aggregate_bundle

    if entity_id in AGGREGATE_IDS and entity_id not in (
        "high-risk-current",
        "command-activity-current",
    ):
        return build_context_aggregate_bundle(aggregate_id=entity_id, request=request)

    base["summary"] = {"title": f"Aggregate · {entity_id}", "aggregate": True}
    base["confidence_score"] = 72.0
    if entity_id == "national-risk-current":
        risk = calculate_national_risk()
        base["summary"] = {
            "title": "Current national risk",
            "score": risk["score"],
            "status": risk["status"],
            "body": "; ".join(risk["reasons"][:4]),
        }
        base["risk_explanation"] = risk_breakdown.national_risk_breakdown()
        base["recommended_actions"] = risk["recommended_actions"]
        base["records"] = [
            {
                "id": str(x.id),
                "score": float(x.national_score),
                "status": x.status,
                "created_at": x.created_at.isoformat(),
            }
            for x in NationalRiskSnapshot.objects.order_by("-created_at")[:12]
        ]
        base["confidence_score"] = risk["confidence"]
        return base

    if entity_id == "high-risk-current":
        qs = NationalIncident.objects.filter(severity__in=["critical", "high"]).order_by("-created_at")[:25]
        base["records"] = [
            {
                "id": str(x.id),
                "code": x.incident_code,
                "title": x.title,
                "severity": x.severity,
                "status": x.status,
            }
            for x in qs
        ]
        return base

    if entity_id == "open-alerts-current":
        qs = NationalAlert.objects.filter(resolved_at__isnull=True).order_by("-created_at")[:30]
        base["records"] = [
            {"id": str(x.id), "title": x.title, "severity": x.severity, "state": x.state} for x in qs
        ]
        return base

    if entity_id == "fraud-flags-current":
        qs = NationalAlert.objects.filter(alert_type__icontains="fraud").order_by("-created_at")[:25]
        base["records"] = [{"id": str(x.id), "title": x.title, "severity": x.severity} for x in qs]
        return base

    if entity_id == "counterfeit-detections-current":
        qs = IntelligenceSignal.objects.filter(
            signal_type__in=[
                IntelligenceSignal.SIGNAL_SUSPICIOUS_SCAN,
                IntelligenceSignal.SIGNAL_CLUSTER,
            ]
        ).order_by("-created_at")[:25]
        base["records"] = [{"id": str(x.id), "title": x.title, "severity": x.severity} for x in qs]
        return base

    if entity_id == "active-investigations-current":
        qs = EnforcementCase.objects.exclude(case_status="closed").order_by("-created_at")[:25]
        base["records"] = [
            {"id": str(x.id), "reference": x.case_reference, "title": x.title, "status": x.case_status} for x in qs
        ]
        return base

    if entity_id == "products-tracked-current":
        qs = Product.objects.order_by("-created_at")[:40]
        base["records"] = [{"id": str(x.id), "name": x.name} for x in qs]
        return base

    if entity_id == "recalls-current":
        qs = BatchRecall.objects.order_by("-effective_at")[:25]
        base["records"] = [{"id": str(x.id), "effective_at": x.effective_at.isoformat() if x.effective_at else ""} for x in qs]
        return base

    if entity_id == "command-activity-current":
        from apps.core.roles import is_regulator_user
        from apps.tenancy.services.tenant import get_user_membership_organisations

        q = ActivityFeedEntry.objects.order_by("-created_at")
        if not is_regulator_user(request.user) and not request.user.is_superuser:
            org_ids = get_user_membership_organisations(request.user)
            q = q.filter(organisation_id__in=org_ids) if org_ids else q.none()
        base["records"] = [
            {
                "id": str(x.id),
                "title": x.title,
                "feed_type": x.feed_type,
                "severity": x.severity,
                "created_at": x.created_at.isoformat(),
                "entity_type": x.entity_type,
                "entity_id": str(x.entity_id) if x.entity_id else None,
            }
            for x in q[:40]
        ]
        return base

    return base


def list_operational_actions(entity_type: str, entity_id: str) -> list[dict]:
    actions = [
        {"id": "create_task", "label": "Create operational task", "requires_confirm": True, "workflow": "task"},
        {"id": "record_acknowledgement", "label": "Acknowledge reviewed", "requires_confirm": False, "workflow": "ack"},
        {"id": "generate_briefing", "label": "Generate intelligence briefing", "requires_confirm": False, "workflow": "briefing"},
    ]
    if entity_type in ("enforcement_recommendation", "national_risk", "alert", "intelligence_signal") or entity_id in AGGREGATE_IDS:
        actions.append({"id": "open_investigation", "label": "Open investigation case", "requires_confirm": True, "workflow": "investigation"})
    if entity_type == "alert":
        actions.append({"id": "escalate_alert", "label": "Escalate alert", "requires_confirm": True, "workflow": "escalation"})
    if entity_type == "enforcement_recommendation":
        actions.append(
            {"id": "mark_false_positive", "label": "Mark recommendation as dismissed", "requires_confirm": True, "workflow": "dismiss"}
        )
    return actions
