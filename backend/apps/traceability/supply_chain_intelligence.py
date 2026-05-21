"""Phase 12 — national supply chain traceability intelligence."""
from __future__ import annotations

from django.utils import timezone

from apps.logistics.models import ColdChainLog, LogisticsShipment, ShipmentCheckpoint
from apps.traceability.models import SupplyChainTransaction


def shipment_timeline(*, tracking_number: str | None = None, limit: int = 30) -> list[dict]:
    qs = LogisticsShipment.objects.select_related(
        "origin_organisation", "destination_organisation", "logistics_provider"
    ).order_by("-created_at")
    if tracking_number:
        qs = qs.filter(tracking_number=tracking_number)
    rows = []
    for s in qs[:limit]:
        checkpoints = ShipmentCheckpoint.objects.filter(shipment=s).order_by("recorded_at")
        route_score = _route_anomaly_score(s)
        rows.append(
            {
                "tracking_number": s.tracking_number,
                "lifecycle_status": s.lifecycle_status,
                "origin": s.origin_organisation.name,
                "destination": s.destination_organisation.name,
                "temperature_controlled": s.temperature_controlled,
                "chain_integrity_verified": s.chain_integrity_verified,
                "departed_at": s.departed_at.isoformat() if s.departed_at else None,
                "delivered_at": s.delivered_at.isoformat() if s.delivered_at else None,
                "route_anomaly_score": route_score,
                "delayed": s.lifecycle_status not in ("delivered", "cancelled")
                and s.departed_at
                and (timezone.now() - s.departed_at).days > 5,
                "checkpoints": [
                    {
                        "latitude": float(c.latitude),
                        "longitude": float(c.longitude),
                        "temperature_c": float(c.temperature_celsius) if c.temperature_celsius else None,
                        "notes": c.condition_notes,
                        "at": c.recorded_at.isoformat() if c.recorded_at else None,
                    }
                    for c in checkpoints[:20]
                ],
                "hierarchy": {"level": "shipment", "children": ["pallet", "carton", "unit"]},
            }
        )
    return rows


def _route_anomaly_score(shipment) -> int:
    score = 0
    if not shipment.chain_integrity_verified:
        score += 25
    if shipment.temperature_controlled and ColdChainLog.objects.filter(
        shipment=shipment, is_breach=True
    ).exists():
        score += 40
    if shipment.departed_at and not shipment.delivered_at:
        if (timezone.now() - shipment.departed_at).days > 7:
            score += 35
    return min(100, score)


def custody_transfer_audit(*, limit: int = 50) -> list[dict]:
    txs = (
        SupplyChainTransaction.objects.select_related("product", "source_organisation", "destination_organisation")
        .order_by("-created_at")[:limit]
    )
    return [
        {
            "audit_reference": str(t.audit_reference),
            "transaction_type": t.transaction_type,
            "product": t.product.name if t.product else None,
            "source": t.source_organisation.name if t.source_organisation else None,
            "destination": t.destination_organisation.name if t.destination_organisation else None,
            "verification_status": t.verification_status,
            "risk_level": t.risk_level,
            "created_at": t.created_at.isoformat(),
        }
        for t in txs
    ]


def customs_clearance_stages() -> list[dict]:
    return [
        {"stage": "manifest_submitted", "label": "Manifest submitted"},
        {"stage": "inspection_scheduled", "label": "Inspection scheduled"},
        {"stage": "hold_review", "label": "Hold review"},
        {"stage": "cleared", "label": "Cleared for distribution"},
        {"stage": "seized", "label": "Seized / quarantine"},
    ]
