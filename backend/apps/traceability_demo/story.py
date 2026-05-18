"""Build national traceability demo story payload for API and UI."""
from __future__ import annotations

from apps.serialization.models import ProductSerial
from apps.traceability.models import BatchRecall, BatchRegulatoryAudit, SerialCustodyEvent, SupplyChainTransaction
from apps.traceability_demo.constants import DEMO_SERIALS, DEMO_TYPE, SERIAL_AUTHENTIC


def build_traceability_story() -> dict:
    hero = (
        ProductSerial.objects.filter(serial_number=SERIAL_AUTHENTIC, metadata__demo_type=DEMO_TYPE)
        .select_related("batch", "batch__product", "custody_organisation")
        .first()
    )

    if not hero:
        return {
            "seeded": False,
            "message": "Run: python manage.py seed_traceability_demo",
            "demo_serials": DEMO_SERIALS,
        }

    batch = hero.batch
    product = batch.product
    custody = list(
        SerialCustodyEvent.objects.filter(product_serial=hero, metadata__demo_type=DEMO_TYPE)
        .order_by("created_at")
        .values("source_node", "destination_node", "custody_confirmed", "integrity_status", "created_at")
    )
    transactions = list(
        SupplyChainTransaction.objects.filter(metadata__demo_type=DEMO_TYPE)
        .order_by("created_at")
        .values("audit_reference", "transaction_type", "verification_status", "created_at")[:20]
    )
    audits = list(
        BatchRegulatoryAudit.objects.filter(batch__metadata__demo_type=DEMO_TYPE)
        .order_by("created_at")
        .values("action", "notes", "created_at")[:10]
    )
    recall = BatchRecall.objects.filter(batch__metadata__demo_type=DEMO_TYPE).first()

    scenarios = []
    for label, sn in DEMO_SERIALS.items():
        row = ProductSerial.objects.filter(serial_number=sn).first()
        scenarios.append(
            {
                "label": label,
                "serial_number": sn,
                "in_registry": row is not None,
                "scenario": (row.metadata or {}).get("scenario") if row else None,
                "batch_number": row.batch.batch_number if row else None,
            }
        )

    return {
        "seeded": True,
        "demo_type": DEMO_TYPE,
        "hero_serial": SERIAL_AUTHENTIC,
        "product": {
            "name": product.name,
            "brand": product.brand_name,
            "code": product.national_product_code,
        },
        "batch": {
            "batch_number": batch.batch_number,
            "regulator_status": batch.regulator_status,
            "lifecycle_status": batch.lifecycle_status,
            "expiry_date": batch.expiry_date.isoformat() if batch.expiry_date else None,
        },
        "lifecycle_timeline": [
            {"step": "manufacturing", "label": "Batch created & regulator approved", "status": "complete"},
            {"step": "serialization", "label": "National serials & QR issued", "status": "complete"},
            {"step": "distribution", "label": "Manufacturer → distributor → warehouse", "status": "complete"},
            {"step": "pharmacy", "label": "Pharmacy receipt & stocking", "status": "complete"},
            {"step": "dispense", "label": "Patient dispense (parallel demo serial)", "status": "complete"},
            {"step": "citizen_verify", "label": "Public authenticity verification", "status": "ready"},
        ],
        "supply_chain_nodes": ["manufacturer", "distributor", "warehouse", "pharmacy", "patient"],
        "custody_chain": custody,
        "transactions": transactions,
        "regulatory_audits": audits,
        "recall": {
            "active": recall is not None,
            "reason": recall.recall_reason if recall else None,
            "batch_number": recall.batch.batch_number if recall else None,
        },
        "suspicious_scan": {
            "serial": DEMO_SERIALS["suspicious"],
            "note": "Elevated counterfeit probability and failed scan history",
        },
        "demo_serials": DEMO_SERIALS,
        "verification_scenarios": scenarios,
        "audit_trail_note": "All records tagged metadata.demo_type=traceability_demo",
    }
