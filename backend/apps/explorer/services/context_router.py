"""Phase 20A — resolve dashboard contexts to concrete explorer entities."""
from __future__ import annotations

from apps.alerts.models import NationalAlert
from apps.command_center.models import NationalIncident
from apps.enforcement.models import EnforcementCase, EnforcementRecommendation
from apps.intelligence.models import CounterfeitCluster, IntelligenceSignal, NationalRiskSnapshot
from apps.notifications.models import Notification
from apps.operations.models import ActivityFeedEntry
from apps.organisations.models import Organisation
from apps.products.models import Product
from apps.scanning.models import ScanEvent
from apps.traceability.models import BatchRecall


def _route(entity_type: str, entity_id: str, *, title: str, subtitle: str = "") -> dict:
    return {
        "entity_type": entity_type,
        "entity_id": str(entity_id),
        "title": title,
        "subtitle": subtitle,
        "resolved": True,
    }


def resolve_context_route(*, context_key: str, user=None) -> dict:
    """
    Map UI context keys to a specific operational entity (not generic national aggregate).
  Falls back to list aggregate only when no rows exist.
    """
    key = (context_key or "").strip().lower().replace("-", "_")

    if key in ("counterfeit_detections", "counterfeit_detection", "counterfeit"):
        cluster = CounterfeitCluster.objects.filter(status="open").order_by("-suspicious_count").first()
        if cluster:
            return _route("counterfeit_cluster", cluster.id, title=f"Cluster {cluster.cluster_code}")
        sig = IntelligenceSignal.objects.filter(is_active=True).order_by("-created_at").first()
        if sig:
            return _route("intelligence_signal", sig.id, title=sig.title)
        return _route("national_risk", "counterfeit-detections-current", title="Counterfeit detections", subtitle="aggregate")

    if key in ("open_alerts", "alert", "alerts"):
        alert = NationalAlert.objects.filter(resolved_at__isnull=True).order_by("-created_at").first()
        if alert:
            return _route("alert", alert.id, title=alert.title)
        return _route("alert", "open-alerts-current", title="Open alerts", subtitle="aggregate")

    if key in ("fraud_flags", "fraud"):
        alert = (
            NationalAlert.objects.filter(alert_type__icontains="fraud")
            .order_by("-created_at")
            .first()
        )
        if alert:
            return _route("alert", alert.id, title=alert.title)
        return _route("national_risk", "fraud-flags-current", title="Fraud flags", subtitle="aggregate")

    if key in ("active_investigations", "investigations", "investigation"):
        case = EnforcementCase.objects.exclude(case_status="closed").order_by("-created_at").first()
        if case:
            return _route("enforcement_case", case.id, title=case.title)
        inc = NationalIncident.objects.exclude(status="resolved").order_by("-created_at").first()
        if inc:
            return _route("incident", inc.id, title=inc.title)
        return _route(
            "national_risk",
            "active-investigations-current",
            title="Active investigations",
            subtitle="aggregate",
        )

    if key in ("recalls", "recall", "emergency_recalls"):
        recall = BatchRecall.objects.order_by("-effective_at").first()
        if recall:
            return _route("recall", recall.id, title="Batch recall")
        return _route("national_risk", "recalls-current", title="Recalls", subtitle="aggregate")

    if key in ("verifications", "verifications_24h", "scans"):
        scan = ScanEvent.objects.order_by("-created_at").first()
        if scan:
            return _route("scan_event", scan.id, title=f"Scan {scan.serial_number[:20]}")
        snap = NationalRiskSnapshot.objects.order_by("-created_at").first()
        if snap:
            return _route("national_risk", str(snap.id), title="National risk snapshot")
        return _route("national_risk", "national-risk-current", title="National risk", subtitle="aggregate")

    if key in ("products_tracked", "products", "product"):
        product = Product.objects.order_by("-created_at").first()
        if product:
            return _route("product", product.id, title=product.name)
        return _route("product", "products-tracked-current", title="Products", subtitle="aggregate")

    if key in ("national_status", "national_risk", "national_threat"):
        snap = NationalRiskSnapshot.objects.order_by("-created_at").first()
        if snap:
            return _route("national_risk", str(snap.id), title="National risk snapshot")
        return _route("national_risk", "national-risk-current", title="National risk", subtitle="aggregate")

    if key in ("command_activity", "activity"):
        entry = ActivityFeedEntry.objects.order_by("-created_at").first()
        if entry and entry.entity_type and entry.entity_id:
            return _route(entry.entity_type, str(entry.entity_id), title=entry.title)
        if entry:
            return _route("task", "command-activity-current", title=entry.title)
        return _route("task", "command-activity-current", title="Command activity", subtitle="aggregate")

    if key in ("enforcement_recommendation", "recommendations"):
        rec = EnforcementRecommendation.objects.filter(
            recommendation_status=EnforcementRecommendation.STATUS_PENDING
        ).first()
        if rec:
            return _route("enforcement_recommendation", rec.id, title=rec.title)
        return _route("national_risk", "national-risk-current", title="Recommendations", subtitle="aggregate")

    if key in ("customs", "customs_seizure", "customs_event"):
        scan = ScanEvent.objects.filter(scan_type=ScanEvent.SCAN_CUSTOMS).order_by("-created_at").first()
        if scan:
            return _route("scan_event", scan.id, title="Customs verification")
        return _route("national_risk", "recalls-current", title="Customs activity", subtitle="aggregate")

    if key in ("pharmacy", "pharmacies"):
        org = Organisation.objects.filter(organisation_type__code="pharmacy").first()
        if org:
            return _route("organisation", org.id, title=org.legal_name)
        return _route("organisation_risk", "national-risk-current", title="Pharmacies", subtitle="aggregate")

    if key in ("manufacturer", "manufacturers"):
        org = Organisation.objects.filter(organisation_type__code="manufacturer").first()
        if org:
            return _route("organisation", org.id, title=org.legal_name)
        return _route("organisation_risk", "national-risk-current", title="Manufacturers", subtitle="aggregate")

    if key in ("notification", "notifications") and user:
        n = Notification.objects.filter(recipient=user).order_by("-created_at").first()
        if n:
            return _route("notification", n.id, title=n.title)

    if key in ("intelligence_feed", "feed_verification"):
        sig = IntelligenceSignal.objects.filter(is_active=True).order_by("-created_at").first()
        if sig:
            return _route("intelligence_signal", sig.id, title=sig.title)

    if key in ("intelligence_feed_customs", "feed_customs"):
        return resolve_context_route(context_key="customs", user=user)

    if key in ("intelligence_feed_shortage", "feed_shortage", "shortage"):
        alert = NationalAlert.objects.filter(alert_type__icontains="shortage").order_by("-created_at").first()
        if alert:
            return _route("alert", alert.id, title=alert.title)
        return _route("national_risk", "national-risk-current", title="Shortage watch", subtitle="aggregate")

    snap = NationalRiskSnapshot.objects.order_by("-created_at").first()
    if snap:
        return _route("national_risk", str(snap.id), title="National intelligence")
    return _route("national_risk", "national-risk-current", title="National overview", subtitle="aggregate")
