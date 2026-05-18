"""Organisation-scoped dashboard aggregates."""
from __future__ import annotations

from apps.products.models import Product, ProductBatch
from apps.scanning.models import ScanEvent
from apps.serialization.models import ProductSerial
from apps.traceability.models import SupplyChainTransaction


def organisation_dashboard(*, organisation_id) -> dict:
    products = Product.objects.filter(manufacturer_id=organisation_id).count()
    batches = ProductBatch.objects.filter(product__manufacturer_id=organisation_id).count()
    serials = ProductSerial.objects.filter(batch__product__manufacturer_id=organisation_id).count()
    movements = SupplyChainTransaction.objects.filter(
        source_organisation_id=organisation_id
    ).count() + SupplyChainTransaction.objects.filter(destination_organisation_id=organisation_id).count()
    scans = ScanEvent.objects.filter(organisation_id=organisation_id).count()

    pharmacy_products = Product.objects.filter(metadata__custody_org=str(organisation_id)).count()

    return {
        "organisation_id": str(organisation_id),
        "products": products,
        "batches": batches,
        "serials": serials,
        "supply_chain_movements": movements,
        "scans": scans,
        "pharmacy_inventory_hint": pharmacy_products,
        "isolated_tenant_view": True,
    }
