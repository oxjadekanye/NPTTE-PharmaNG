"""Phase 13 — seed end-to-end national traceability demo chain."""
from __future__ import annotations

import uuid
from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.core.constants import (
    BatchLifecycleStatus,
    BatchRegulatoryAuditAction,
    RegulatorBatchStatus,
    SupplyChainTransactionType,
    VerificationOutcome,
    VerificationStatus,
)
from apps.distributors.models import DistributorProfile, Warehouse
from apps.manufacturers.models import ManufacturerProfile, ManufacturingSite
from apps.organisations.models import Organisation, OrganisationType
from apps.pharmacies.models import PharmacyProfile
from apps.products.models import Product, ProductBatch
from apps.products.services import issue_national_batch_recall
from apps.serialization.models import ProductSerial, SerialScanRecord
from apps.serialization.services import ensure_qr_payload
from apps.traceability.models import (
    BatchRecall,
    BatchRegulatoryAudit,
    RecallExecutionCampaign,
    SerialCustodyEvent,
    SupplyChainTransaction,
)
from apps.traceability.regulatory_audit import log_batch_regulatory_audit
from apps.traceability_demo.constants import (
    DEMO_TYPE,
    SERIAL_AUTHENTIC,
    SERIAL_EXPIRED,
    SERIAL_RECALLED,
    SERIAL_SUSPICIOUS,
    demo_meta,
)
from apps.verification.models import VerificationEvent, VerificationScanLog


def _is_seeded() -> bool:
    return Product.objects.filter(
        national_product_code="TD-DEMO-PARACETAMOL-500",
        metadata__demo_type=DEMO_TYPE,
    ).exists()


def _org_type(code: str, name: str) -> OrganisationType:
    ot, _ = OrganisationType.objects.get_or_create(code=code, defaults={"name": name})
    return ot


def _organisation(
    *,
    type_code: str,
    type_name: str,
    legal_name: str,
    slug: str,
    state: str,
    city: str = "",
    lat: Decimal | None = None,
    lon: Decimal | None = None,
) -> Organisation:
    org, created = Organisation.objects.get_or_create(
        legal_name=legal_name,
        defaults={
            "organisation_type": _org_type(type_code, type_name),
            "trading_name": legal_name.split(" Ltd")[0],
            "state": state,
            "city": city or state,
            "latitude": lat,
            "longitude": lon,
            "metadata": demo_meta(demo_slug=slug),
        },
    )
    if not created and org.metadata.get("demo_type") != DEMO_TYPE:
        org.metadata = {**(org.metadata or {}), **demo_meta(demo_slug=slug)}
        org.save(update_fields=["metadata", "updated_at"])
    return org


def _product(*, org: Organisation, code: str, name: str, brand: str, ingredient: str) -> Product:
    product, created = Product.objects.get_or_create(
        national_product_code=code,
        defaults={
            "name": name,
            "brand_name": brand,
            "active_ingredient": ingredient,
            "strength": "500mg",
            "dosage_form": "Tablet",
            "manufacturer": org,
            "metadata": demo_meta(demo_slug=f"product_{code}"),
        },
    )
    return product


def _batch(
    *,
    product: Product,
    batch_number: str,
    site: ManufacturingSite,
    expiry_days: int,
    slug: str,
    lifecycle: str = BatchLifecycleStatus.ACTIVE,
) -> ProductBatch:
    today = timezone.now().date()
    batch, created = ProductBatch.objects.get_or_create(
        product=product,
        batch_number=batch_number,
        defaults={
            "manufacturing_site": site,
            "manufacturing_date": today - timedelta(days=30),
            "expiry_date": today + timedelta(days=expiry_days),
            "quantity_produced": 5000,
            "regulator_status": RegulatorBatchStatus.APPROVED,
            "lifecycle_status": lifecycle,
            "metadata": demo_meta(demo_slug=slug),
        },
    )
    if not created:
        batch.regulator_status = RegulatorBatchStatus.APPROVED
        batch.lifecycle_status = lifecycle
        batch.expiry_date = today + timedelta(days=expiry_days)
        batch.save(update_fields=["regulator_status", "lifecycle_status", "expiry_date", "updated_at"])
    return batch


def _serial(
    *,
    batch: ProductBatch,
    serial_number: str,
    scenario: str,
    custody: Organisation | None = None,
    dispensed: bool = False,
    scan_count: int = 0,
    counterfeit_probability: Decimal = Decimal("0"),
) -> ProductSerial:
    serial, _ = ProductSerial.objects.get_or_create(
        serial_number=serial_number,
        defaults={
            "batch": batch,
            "metadata": demo_meta(scenario=scenario),
            "custody_organisation": custody,
            "is_dispensed": dispensed,
            "scan_count": scan_count,
            "counterfeit_probability": counterfeit_probability,
        },
    )
    serial.batch = batch
    serial.metadata = demo_meta(scenario=scenario)
    serial.custody_organisation = custody
    serial.is_dispensed = dispensed
    serial.scan_count = scan_count
    serial.counterfeit_probability = counterfeit_probability
    serial.save(
        update_fields=[
            "batch",
            "metadata",
            "custody_organisation",
            "is_dispensed",
            "scan_count",
            "counterfeit_probability",
            "updated_at",
        ]
    )
    ensure_qr_payload(serial)
    return serial


def _custody(
    *,
    serial: ProductSerial,
    source_node: str,
    dest_node: str,
    source_org: Organisation | None,
    dest_org: Organisation,
    tx: SupplyChainTransaction | None = None,
) -> SerialCustodyEvent:
    event, _ = SerialCustodyEvent.objects.get_or_create(
        product_serial=serial,
        destination_node=dest_node,
        source_node=source_node,
        destination_organisation=dest_org,
        defaults={
            "source_organisation": source_org,
            "custody_confirmed": True,
            "integrity_status": "verified",
            "supply_chain_transaction": tx,
            "metadata": demo_meta(step=f"{source_node}_to_{dest_node}"),
        },
    )
    return event


def _tx(
    *,
    tx_type: str,
    source: Organisation | None,
    dest: Organisation | None,
    product: Product,
    batch: ProductBatch | None = None,
    serial: ProductSerial | None = None,
    slug: str,
) -> SupplyChainTransaction:
    ref = uuid.uuid5(uuid.NAMESPACE_DNS, f"td-demo-{slug}")
    tx, _ = SupplyChainTransaction.objects.get_or_create(
        audit_reference=ref,
        defaults={
            "transaction_type": tx_type,
            "source_organisation": source,
            "destination_organisation": dest,
            "product": product,
            "batch": batch,
            "product_serial": serial,
            "quantity_delta": 1,
            "verification_status": VerificationStatus.VERIFIED,
            "metadata": demo_meta(demo_slug=slug),
        },
    )
    return tx


@transaction.atomic
def seed_traceability_demo(*, force: bool = False) -> dict:
    if _is_seeded() and not force:
        return {
            "status": "already_seeded",
            "demo_type": DEMO_TYPE,
            "serials": {
                "authentic": SERIAL_AUTHENTIC,
                "recalled": SERIAL_RECALLED,
                "suspicious": SERIAL_SUSPICIOUS,
                "expired": SERIAL_EXPIRED,
            },
        }

    # —— Manufacturers (2) ——
    mfg1_org = _organisation(
        type_code="manufacturer",
        type_name="Manufacturer",
        legal_name="TD Demo Pharma Industries Ltd",
        slug="mfg_lagos",
        state="Lagos",
        city="Ikeja",
        lat=Decimal("6.6018"),
        lon=Decimal("3.3515"),
    )
    mfg2_org = _organisation(
        type_code="manufacturer",
        type_name="Manufacturer",
        legal_name="TD Demo Northern Formulations Ltd",
        slug="mfg_kano",
        state="Kano",
        city="Kano",
        lat=Decimal("12.0022"),
        lon=Decimal("8.5920"),
    )
    mfg1_profile, _ = ManufacturerProfile.objects.get_or_create(
        organisation=mfg1_org,
        defaults={"metadata": demo_meta(demo_slug="mfg_profile_1")},
    )
    mfg2_profile, _ = ManufacturerProfile.objects.get_or_create(
        organisation=mfg2_org,
        defaults={"metadata": demo_meta(demo_slug="mfg_profile_2")},
    )
    site1, _ = ManufacturingSite.objects.get_or_create(
        manufacturer=mfg1_profile,
        site_code="TD-LG-01",
        defaults={"site_name": "Lagos Serialization Plant", "metadata": demo_meta()},
    )
    site2, _ = ManufacturingSite.objects.get_or_create(
        manufacturer=mfg2_profile,
        site_code="TD-KN-01",
        defaults={"site_name": "Kano Formulation Unit", "metadata": demo_meta()},
    )

    # —— Products (3) ——
    product_para = _product(
        org=mfg1_org,
        code="TD-DEMO-PARACETAMOL-500",
        name="Paracetamol",
        brand="TD Panadol",
        ingredient="Paracetamol",
    )
    product_amox = _product(
        org=mfg1_org,
        code="TD-DEMO-AMOXICILLIN-500",
        name="Amoxicillin",
        brand="TD Amoxil",
        ingredient="Amoxicillin",
    )
    product_met = _product(
        org=mfg2_org,
        code="TD-DEMO-METFORMIN-500",
        name="Metformin",
        brand="TD Glucophage",
        ingredient="Metformin",
    )

    # —— Supply chain nodes ——
    dist_org = _organisation(
        type_code="distributor",
        type_name="Distributor",
        legal_name="TD Demo National Distributors Ltd",
        slug="distributor",
        state="Lagos",
        lat=Decimal("6.5244"),
        lon=Decimal("3.3792"),
    )
    dist_profile, _ = DistributorProfile.objects.get_or_create(
        organisation=dist_org,
        defaults={"wholesale_license": "TD-WHL-001", "metadata": demo_meta()},
    )
    wh_org = _organisation(
        type_code="logistics",
        type_name="Logistics",
        legal_name="TD Demo Cold Chain Warehouse Ltd",
        slug="warehouse",
        state="Lagos",
        city="Apapa",
        lat=Decimal("6.4483"),
        lon=Decimal("3.3903"),
    )
    warehouse, _ = Warehouse.objects.get_or_create(
        organisation=wh_org,
        warehouse_code="TD-WH-APAPA",
        defaults={
            "distributor": dist_profile,
            "name": "Apapa National Depot",
            "state": "Lagos",
            "cold_chain_enabled": True,
            "metadata": demo_meta(),
        },
    )
    pharm_org = _organisation(
        type_code="pharmacy",
        type_name="Pharmacy",
        legal_name="TD Demo Ikeja Community Pharmacy Ltd",
        slug="pharmacy",
        state="Lagos",
        city="Ikeja",
        lat=Decimal("6.5958"),
        lon=Decimal("3.3421"),
    )
    PharmacyProfile.objects.get_or_create(
        organisation=pharm_org,
        defaults={
            "pharmacy_license_number": "TD-PH-LG-001",
            "is_national_registry_verified": True,
            "metadata": demo_meta(),
        },
    )

    # —— Batches ——
    hero_batch = _batch(
        product=product_para,
        batch_number="TD-BATCH-HERO-2026-001",
        site=site1,
        expiry_days=365,
        slug="batch_hero",
    )
    recall_batch = _batch(
        product=product_amox,
        batch_number="TD-BATCH-RECALL-2026-001",
        site=site1,
        expiry_days=300,
        slug="batch_recall",
    )
    expired_batch = _batch(
        product=product_para,
        batch_number="TD-BATCH-EXP-2025-001",
        site=site1,
        expiry_days=-30,
        slug="batch_expired",
        lifecycle=BatchLifecycleStatus.EXPIRED,
    )
    expired_batch.expiry_date = timezone.now().date() - timedelta(days=60)
    expired_batch.lifecycle_status = BatchLifecycleStatus.EXPIRED
    expired_batch.save(update_fields=["expiry_date", "lifecycle_status", "updated_at"])

    susp_batch = _batch(
        product=product_met,
        batch_number="TD-BATCH-SUSP-2026-001",
        site=site2,
        expiry_days=400,
        slug="batch_suspicious",
    )

    for batch in (hero_batch, recall_batch, expired_batch, susp_batch):
        log_batch_regulatory_audit(
            batch=batch,
            action=BatchRegulatoryAuditAction.APPROVED,
            actor=None,
            notes="TD demo batch approval",
            payload=demo_meta(),
        )

    # —— Serials ——
    hero_serial = _serial(
        batch=hero_batch,
        serial_number=SERIAL_AUTHENTIC,
        scenario="authentic",
        custody=pharm_org,
        dispensed=False,
    )
    recalled_serial = _serial(
        batch=recall_batch,
        serial_number=SERIAL_RECALLED,
        scenario="recalled",
        custody=pharm_org,
    )
    expired_serial = _serial(
        batch=expired_batch,
        serial_number=SERIAL_EXPIRED,
        scenario="expired",
        custody=pharm_org,
    )
    suspicious_serial = _serial(
        batch=susp_batch,
        serial_number=SERIAL_SUSPICIOUS,
        scenario="suspicious",
        custody=pharm_org,
        counterfeit_probability=Decimal("82"),
        scan_count=80,
    )

    dispensed_serial = _serial(
        batch=hero_batch,
        serial_number="NG-NPTTE-TD-PARACETAMOL-2026-DISP000001",
        scenario="dispensed",
        custody=pharm_org,
        dispensed=True,
    )

    # Extra generated serials for serialization volume
    for i in range(2, 6):
        sn = f"NG-NPTTE-TD-PARACETAMOL-2026-AUTH{i:09d}"
        _serial(batch=hero_batch, serial_number=sn, scenario="authentic_pool", custody=wh_org)

    # —— Recall ——
    if not BatchRecall.objects.filter(batch=recall_batch, metadata__demo_type=DEMO_TYPE).exists():
        issue_national_batch_recall(
            batch=recall_batch,
            actor=None,
            reason="TD demo — nationwide precautionary recall (simulation).",
            issued_by_organisation=mfg1_org,
        )
        recall = BatchRecall.objects.filter(batch=recall_batch).latest("created_at")
        recall.metadata = demo_meta(scenario="recall")
        recall.save(update_fields=["metadata", "updated_at"])
        campaign, _ = RecallExecutionCampaign.objects.get_or_create(
            batch_recall=recall,
            campaign_code="TD-RECALL-CAMP-001",
            defaults={
                "pharmacies_targeted": 120,
                "pharmacies_acknowledged": 45,
                "estimated_patient_exposure": 3200,
                "metadata": demo_meta(),
            },
        )

    # —— Supply chain movement (hero serial journey) ——
    tx_mfg = _tx(
        tx_type=SupplyChainTransactionType.MANUFACTURER_DISPATCH,
        source=mfg1_org,
        dest=dist_org,
        product=product_para,
        batch=hero_batch,
        serial=hero_serial,
        slug="tx_mfg_dispatch",
    )
    tx_dist_wh = _tx(
        tx_type=SupplyChainTransactionType.DISTRIBUTOR_DISPATCH,
        source=dist_org,
        dest=wh_org,
        product=product_para,
        batch=hero_batch,
        serial=hero_serial,
        slug="tx_dist_warehouse",
    )
    tx_wh_pharm = _tx(
        tx_type=SupplyChainTransactionType.PHARMACY_STOCKING,
        source=wh_org,
        dest=pharm_org,
        product=product_para,
        batch=hero_batch,
        serial=hero_serial,
        slug="tx_pharmacy_receipt",
    )
    tx_sale = _tx(
        tx_type=SupplyChainTransactionType.PHARMACY_SALE,
        source=pharm_org,
        dest=None,
        product=product_para,
        batch=hero_batch,
        serial=dispensed_serial,
        slug="tx_pharmacy_dispense",
    )

    _custody(
        serial=hero_serial,
        source_node=SerialCustodyEvent.NODE_MANUFACTURER,
        dest_node=SerialCustodyEvent.NODE_DISTRIBUTOR,
        source_org=mfg1_org,
        dest_org=dist_org,
        tx=tx_mfg,
    )
    _custody(
        serial=hero_serial,
        source_node=SerialCustodyEvent.NODE_DISTRIBUTOR,
        dest_node=SerialCustodyEvent.NODE_WAREHOUSE,
        source_org=dist_org,
        dest_org=wh_org,
        tx=tx_dist_wh,
    )
    _custody(
        serial=hero_serial,
        source_node=SerialCustodyEvent.NODE_WAREHOUSE,
        dest_node=SerialCustodyEvent.NODE_PHARMACY,
        source_org=wh_org,
        dest_org=pharm_org,
        tx=tx_wh_pharm,
    )
    _custody(
        serial=dispensed_serial,
        source_node=SerialCustodyEvent.NODE_PHARMACY,
        dest_node=SerialCustodyEvent.NODE_PATIENT,
        source_org=pharm_org,
        dest_org=pharm_org,
        tx=tx_sale,
    )

    # —— Scan records ——
    SerialScanRecord.objects.get_or_create(
        serial_number=hero_serial.serial_number,
        replay_nonce="td-demo-pharm-receipt",
        defaults={
            "product_serial": hero_serial,
            "scan_source": "pharmacy_receive",
            "scanner_type": "mobile_camera",
            "outcome": "received",
            "device_fingerprint": "td-demo-device",
            "metadata": demo_meta(scenario="pharmacy_receipt"),
        },
    )
    SerialScanRecord.objects.get_or_create(
        serial_number=dispensed_serial.serial_number,
        replay_nonce="td-demo-pharm-dispense",
        defaults={
            "product_serial": dispensed_serial,
            "scan_source": "pharmacy_dispense",
            "scanner_type": "mobile_camera",
            "outcome": "dispensed",
            "device_fingerprint": "td-demo-device",
            "metadata": demo_meta(scenario="pharmacy_dispense"),
        },
    )
    SerialScanRecord.objects.get_or_create(
        serial_number=suspicious_serial.serial_number,
        replay_nonce="td-demo-suspicious-scan",
        defaults={
            "product_serial": suspicious_serial,
            "scan_source": "citizen_verify",
            "scanner_type": "public_verify",
            "outcome": "counterfeit_suspected",
            "is_suspicious": True,
            "device_fingerprint": "td-demo-suspicious",
            "metadata": demo_meta(scenario="suspicious_scan"),
        },
    )

    # —— Citizen verification examples ——
    VerificationScanLog.objects.get_or_create(
        serial_number=hero_serial.serial_number,
        outcome=VerificationOutcome.AUTHENTIC,
        device_fingerprint="td-demo-citizen-auth",
        defaults={
            "product_serial": hero_serial,
            "metadata": demo_meta(scenario="citizen_authentic"),
        },
    )
    VerificationScanLog.objects.get_or_create(
        serial_number=recalled_serial.serial_number,
        outcome=VerificationOutcome.RECALLED,
        device_fingerprint="td-demo-citizen-recall",
        defaults={
            "product_serial": recalled_serial,
            "metadata": demo_meta(scenario="citizen_recalled"),
        },
    )
    VerificationEvent.objects.get_or_create(
        product_serial=hero_serial,
        channel="qr",
        is_authentic=True,
        defaults={
            "verification_message": "TD demo — authentic verification",
            "metadata": demo_meta(scenario="citizen_event"),
        },
    )

    for _ in range(5):
        VerificationScanLog.objects.get_or_create(
            serial_number=suspicious_serial.serial_number,
            outcome=VerificationOutcome.COUNTERFEIT_SUSPECTED,
            device_fingerprint=f"td-demo-fail-{_}",
            defaults={
                "product_serial": suspicious_serial,
                "metadata": demo_meta(scenario="suspicious_history"),
            },
        )

    return {
        "status": "seeded",
        "demo_type": DEMO_TYPE,
        "manufacturers": 2,
        "products": 3,
        "batches": 4,
        "serials": {
            "authentic": SERIAL_AUTHENTIC,
            "recalled": SERIAL_RECALLED,
            "suspicious": SERIAL_SUSPICIOUS,
            "expired": SERIAL_EXPIRED,
            "dispensed": dispensed_serial.serial_number,
        },
        "organisations": {
            "manufacturer": str(mfg1_org.id),
            "distributor": str(dist_org.id),
            "warehouse": str(wh_org.id),
            "pharmacy": str(pharm_org.id),
        },
    }
