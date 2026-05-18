"""Phase 13 — remove only traceability_demo tagged records."""
from __future__ import annotations

from django.db import transaction

from apps.distributors.models import DistributorProfile, Warehouse
from apps.manufacturers.models import ManufacturerProfile, ManufacturingSite
from apps.organisations.models import Organisation
from apps.pharmacies.models import PharmacyProfile
from apps.products.models import Product, ProductBatch
from apps.scanning.models import ScanEvent
from apps.serialization.models import ProductSerial, SerialScanRecord
from apps.traceability.models import (
    BatchRecall,
    BatchRegulatoryAudit,
    PharmacyRecallAcknowledgement,
    RecallExecutionCampaign,
    SerialCustodyEvent,
    SupplyChainTransaction,
)
from apps.traceability_demo.constants import DEMO_TYPE
from apps.verification.models import VerificationEvent, VerificationScanLog


def _demo_qs(model):
    return model.objects.filter(metadata__demo_type=DEMO_TYPE)


def _demo_serial_numbers():
    return list(
        ProductSerial.objects.filter(metadata__demo_type=DEMO_TYPE).values_list(
            "serial_number", flat=True
        )
    )


@transaction.atomic
def clear_traceability_demo() -> dict:
    serials = _demo_serial_numbers()
    counts = {}

    counts["scan_events"] = _demo_qs(ScanEvent).delete()[0]
    counts["verification_events"] = VerificationEvent.objects.filter(
        product_serial__metadata__demo_type=DEMO_TYPE
    ).delete()[0]
    counts["verification_scan_logs"] = VerificationScanLog.objects.filter(
        serial_number__in=serials
    ).delete()[0] if serials else 0
    counts["serial_scan_records"] = _demo_qs(SerialScanRecord).delete()[0]
    counts["custody_events"] = _demo_qs(SerialCustodyEvent).delete()[0]
    counts["pharmacy_recall_acks"] = _demo_qs(PharmacyRecallAcknowledgement).delete()[0]
    counts["recall_campaigns"] = _demo_qs(RecallExecutionCampaign).delete()[0]
    counts["batch_recalls"] = _demo_qs(BatchRecall).delete()[0]
    counts["batch_regulatory_audits"] = BatchRegulatoryAudit.objects.filter(
        batch__metadata__demo_type=DEMO_TYPE
    ).delete()[0]
    counts["supply_chain_transactions"] = _demo_qs(SupplyChainTransaction).delete()[0]
    counts["product_serials"] = _demo_qs(ProductSerial).delete()[0]
    counts["product_batches"] = _demo_qs(ProductBatch).delete()[0]
    counts["products"] = _demo_qs(Product).delete()[0]
    counts["warehouses"] = _demo_qs(Warehouse).delete()[0]
    counts["pharmacy_profiles"] = _demo_qs(PharmacyProfile).delete()[0]
    counts["distributor_profiles"] = _demo_qs(DistributorProfile).delete()[0]
    counts["manufacturing_sites"] = _demo_qs(ManufacturingSite).delete()[0]
    counts["manufacturer_profiles"] = _demo_qs(ManufacturerProfile).delete()[0]
    counts["organisations"] = _demo_qs(Organisation).delete()[0]

    return {"cleared": counts, "demo_type": DEMO_TYPE}
