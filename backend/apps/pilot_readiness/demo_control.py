"""Safe pilot demo data operations — only records tagged metadata.pilot_demo=true."""
from __future__ import annotations

import uuid
from datetime import timedelta

from django.utils import timezone

from apps.command_center.models import NationalIncident
from apps.organisations.models import Organisation
from apps.products.models import Product, ProductBatch
from apps.serialization.models import ProductSerial

DEMO_TAG = "pilot_demo"


def _demo_filter(qs):
    return qs.filter(metadata__pilot_demo=True)


def demo_inventory() -> dict:
    return {
        "demo_organisations": _demo_filter(Organisation.objects.all()).count(),
        "demo_products": _demo_filter(Product.objects.all()).count(),
        "demo_batches": _demo_filter(ProductBatch.objects.all()).count(),
        "demo_serials": _demo_filter(ProductSerial.objects.all()).count(),
        "demo_incidents": NationalIncident.objects.filter(incident_code__startswith="DEMO-").count(),
        "simulated_intelligence": "frontend_bus_and_demo_constants",
        "warning": "Clear operations ONLY remove records tagged pilot_demo or DEMO- incident codes.",
    }


def seed_demo_products(*, actor=None) -> dict:
    from apps.organisations.models import OrganisationType

    org_type, _ = OrganisationType.objects.get_or_create(
        code="MANUFACTURER",
        defaults={"name": "Manufacturer", "description": "Pilot demo type"},
    )
    org, _ = Organisation.objects.get_or_create(
        legal_name="DEMO Lagos Pharma Industries Ltd",
        defaults={
            "organisation_type": org_type,
            "trading_name": "DEMO Lagos Pharma",
            "state": "Lagos",
            "metadata": {DEMO_TAG: True},
            "created_by": actor,
        },
    )
    if DEMO_TAG not in (org.metadata or {}):
        org.metadata = {**(org.metadata or {}), DEMO_TAG: True}
        org.save(update_fields=["metadata", "updated_at"])

    product, _ = Product.objects.get_or_create(
        national_product_code="DEMO-PARACETAMOL-500",
        defaults={
            "name": "DEMO Paracetamol 500mg",
            "active_ingredient": "Paracetamol",
            "strength": "500mg",
            "manufacturer": org,
            "metadata": {DEMO_TAG: True, "label": "SIMULATED"},
            "created_by": actor,
        },
    )
    batch, _ = ProductBatch.objects.get_or_create(
        batch_number=f"DEMO-BATCH-{uuid.uuid4().hex[:8].upper()}",
        product=product,
        defaults={
            "manufacturing_date": timezone.now().date(),
            "expiry_date": timezone.now().date() + timedelta(days=365),
            "metadata": {DEMO_TAG: True},
            "created_by": actor,
        },
    )
    return {
        "organisation_id": str(org.id),
        "product_id": str(product.id),
        "batch_id": str(batch.id),
        "marked": "DEMO/SIMULATED",
    }


def seed_demo_incident(*, actor=None) -> dict:
    code = f"DEMO-INC-{uuid.uuid4().hex[:6].upper()}"
    inc = NationalIncident.objects.create(
        incident_code=code,
        title="DEMO/SIMULATED — Counterfeit cluster drill",
        description="Pilot demonstration incident only.",
        severity="high",
        status="open",
        threat_score=75,
        metadata={DEMO_TAG: True},
        created_by=actor,
    )
    return {"incident_code": inc.incident_code, "marked": "DEMO/SIMULATED"}


def clear_demo_data() -> dict:
    """Delete only explicitly tagged demo records."""
    counts = {
        "serials": _demo_filter(ProductSerial.objects.all()).delete()[0],
        "batches": _demo_filter(ProductBatch.objects.all()).delete()[0],
        "products": _demo_filter(Product.objects.all()).delete()[0],
        "organisations": _demo_filter(Organisation.objects.all()).delete()[0],
        "incidents": NationalIncident.objects.filter(incident_code__startswith="DEMO-").delete()[0],
    }
    return {"cleared": counts, "note": "Production records without pilot_demo tag were not touched."}
