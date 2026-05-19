"""Idempotent national-scale operational demo seed (Phase 20A.2)."""
from __future__ import annotations

import random
import uuid
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import Role
from apps.alerts.models import NationalAlert
from apps.core.constants import RoleCode
from apps.enforcement.models import EnforcementCase
from apps.enforcement.services.cases import create_enforcement_case
from apps.intelligence.models import CounterfeitCluster, IntelligenceSignal, NationalRiskSnapshot
from apps.operational_demo.constants import (
    DEMO_TYPE,
    EVENT_CATEGORIES,
    NIGERIAN_LOCATIONS,
    PRODUCT_CATALOG,
    STAFF_PROFILES,
    demo_meta,
)
from apps.organisations.models import Organisation, OrganisationType
from apps.products.models import Product, ProductBatch
from apps.scanning.models import ScanEvent
from apps.serialization.models import ProductSerial

User = get_user_model()

RNG = random.Random(42)

ORG_SPECS = [
    ("pharmacy", 40, "Pharmacy"),
    ("manufacturer", 15, "Manufacturer"),
    ("distributor", 20, "Distributor"),
    ("warehouse", 12, "Warehouse"),
    ("customs", 8, "Customs checkpoint"),
    ("hospital", 12, "Hospital"),
    ("regulator", 6, "Regulator unit"),
    ("enforcement", 6, "Enforcement team"),
]

LITE_SCALE = {
    "pharmacy": 5,
    "manufacturer": 3,
    "distributor": 3,
    "warehouse": 2,
    "customs": 2,
    "hospital": 2,
    "regulator": 2,
    "enforcement": 2,
    "products": 12,
    "batches_per_product": 2,
    "serials": 120,
    "scans": 80,
    "event_multiplier": 0.08,
    "staff": 8,
}

FULL_SCALE = {
    "pharmacy": 40,
    "manufacturer": 15,
    "distributor": 20,
    "warehouse": 12,
    "customs": 8,
    "hospital": 12,
    "regulator": 6,
    "enforcement": 6,
    "products": 60,
    "batches_per_product": 3,
    "serials": 3000,
    "scans": 2000,
    "event_multiplier": 1.0,
    "staff": 30,
}


def is_seeded() -> bool:
    return Product.objects.filter(metadata__demo_type=DEMO_TYPE).exists()


def _scale(lite: bool) -> dict:
    return LITE_SCALE if lite else FULL_SCALE


def _loc(i: int):
    return NIGERIAN_LOCATIONS[i % len(NIGERIAN_LOCATIONS)]


def _org_type(code: str) -> OrganisationType:
    ot, _ = OrganisationType.objects.get_or_create(
        code=code,
        defaults={"name": code.replace("_", " ").title(), "metadata": demo_meta()},
    )
    return ot


def _ensure_staff(scale: dict) -> list[User]:
    role, _ = Role.objects.get_or_create(code=RoleCode.NAFDAC_ADMIN, defaults={"name": "NAFDAC Admin"})
    staff: list[User] = []
    profiles = STAFF_PROFILES * 3
    for i in range(min(scale["staff"], len(profiles) * 3)):
        name, role_title, state, team, spec = profiles[i % len(profiles)]
        uname = f"demo_staff_{i + 1}"
        user, created = User.objects.get_or_create(
            username=uname,
            defaults={
                "email": f"{uname}@demo.nptte.ng",
                "first_name": name.split(". ", 1)[-1].split()[0] if ". " in name else name.split()[0],
                "last_name": name.split()[-1],
                "is_regulator": True,
                "role": role,
                "metadata": demo_meta(
                    staff_profile={
                        "full_name": name,
                        "role_title": role_title,
                        "region_state": state,
                        "team": team,
                        "specialisation": spec,
                        "phone": f"+23480{RNG.randint(10000000, 99999999)}",
                        "availability": "available",
                    },
                ),
            },
        )
        if not created:
            user.is_regulator = True
            user.metadata = demo_meta(
                staff_profile=user.metadata.get("staff_profile", {})
                if isinstance(user.metadata, dict)
                else {},
            )
            user.save(update_fields=["is_regulator", "metadata", "updated_at"])
        staff.append(user)
    return staff


@transaction.atomic
def seed_operational_demo_data(*, lite: bool = False, force: bool = False) -> dict:
    if is_seeded() and not force:
        return {"status": "already_seeded", "demo_type": DEMO_TYPE}

    scale = _scale(lite)
    now = timezone.now()
    counts: dict[str, int] = {}

    staff = _ensure_staff(scale)
    counts["staff"] = len(staff)

    orgs_by_type: dict[str, list[Organisation]] = {}
    idx = 0
    for code, full_n, label in ORG_SPECS:
        n = scale.get(code, full_n) if lite else full_n
        ot = _org_type(code)
        orgs: list[Organisation] = []
        for j in range(n):
            state, city, lat, lon = _loc(idx)
            idx += 1
            legal = f"Demo {label} {state} #{j + 1}"
            org, _ = Organisation.objects.get_or_create(
                legal_name=legal,
                defaults={
                    "organisation_type": ot,
                    "trading_name": legal,
                    "registration_number": f"DEMO-{code[:3].upper()}-{idx:04d}",
                    "phone_number": f"+23470{RNG.randint(10000000, 99999999)}",
                    "address_line_1": f"{RNG.randint(1, 120)} Industrial Road",
                    "city": city,
                    "state": state,
                    "latitude": Decimal(str(round(lat + RNG.uniform(-0.05, 0.05), 6))),
                    "longitude": Decimal(str(round(lon + RNG.uniform(-0.05, 0.05), 6))),
                    "metadata": demo_meta(organisation_type_code=code, contact_person=f"Contact {j + 1}"),
                },
            )
            orgs.append(org)
        orgs_by_type[code] = orgs
        counts[f"orgs_{code}"] = len(orgs)

    manufacturers = orgs_by_type.get("manufacturer", [])
    pharmacies = orgs_by_type.get("pharmacy", [])
    products: list[Product] = []
    catalog = PRODUCT_CATALOG * (scale["products"] // len(PRODUCT_CATALOG) + 1)
    for i in range(scale["products"]):
        name, category, strength, form = catalog[i]
        mfr = manufacturers[i % len(manufacturers)] if manufacturers else None
        pcode = f"DEMO-NPC-{i + 1:04d}"
        product, _ = Product.objects.get_or_create(
            national_product_code=pcode,
            defaults={
                "name": name,
                "strength": strength,
                "dosage_form": form,
                "manufacturer": mfr,
                "metadata": demo_meta(category=category),
            },
        )
        products.append(product)
    counts["products"] = len(products)

    batches: list[ProductBatch] = []
    statuses = ["approved", "active", "suspended", "recalled", "expired", "destroyed", "pending_review"]
    for pi, product in enumerate(products):
        for bi in range(scale["batches_per_product"]):
            bnum = f"DEMO-B-{pi + 1:03d}-{bi + 1:02d}"
            batch, _ = ProductBatch.objects.get_or_create(
                product=product,
                batch_number=bnum,
                defaults={
                    "manufacturing_date": (now - timedelta(days=RNG.randint(30, 400))).date(),
                    "expiry_date": (now + timedelta(days=RNG.randint(-60, 500))).date(),
                    "quantity_produced": RNG.randint(500, 5000),
                    "regulator_status": RNG.choice(statuses),
                    "lifecycle_status": RNG.choice(statuses),
                    "metadata": demo_meta(),
                },
            )
            batches.append(batch)
    counts["batches"] = len(batches)

    serials_created = 0
    serial_buf: list[ProductSerial] = []
    target_serials = scale["serials"]
    for batch in batches:
        if serials_created >= target_serials:
            break
        per_batch = min(25, target_serials - serials_created)
        for si in range(per_batch):
            sn = f"NG-DEMO-{batch.batch_number}-{si + 1:05d}"
            if ProductSerial.objects.filter(serial_number=sn).exists():
                continue
            serial_buf.append(
                ProductSerial(
                    batch=batch,
                    serial_number=sn,
                    is_dispensed=RNG.random() < 0.3,
                    counterfeit_probability=Decimal(str(RNG.choice([0, 0, 5, 15, 45, 80]))),
                    metadata=demo_meta(),
                )
            )
            serials_created += 1
            if len(serial_buf) >= 500:
                ProductSerial.objects.bulk_create(serial_buf, ignore_conflicts=True)
                serial_buf = []
    if serial_buf:
        ProductSerial.objects.bulk_create(serial_buf, ignore_conflicts=True)
    counts["serials"] = serials_created

    scan_buf: list[ScanEvent] = []
    scan_types = [
        ScanEvent.SCAN_CITIZEN,
        ScanEvent.SCAN_PHARMACY_DISPENSE,
        ScanEvent.SCAN_WAREHOUSE,
        ScanEvent.SCAN_CUSTOMS,
        ScanEvent.SCAN_REGULATOR,
    ]
    outcomes = ["authentic", "suspicious", "invalid", "recalled", "duplicate", "expired"]
    for i in range(scale["scans"]):
        org = RNG.choice(pharmacies + orgs_by_type.get("warehouse", []) + orgs_by_type.get("customs", []))
        state, city, lat, lon = _loc(i)
        scan_buf.append(
            ScanEvent(
                serial_number=f"NG-DEMO-SCAN-{i + 1:06d}",
                scan_type=RNG.choice(scan_types),
                organisation=org,
                latitude=Decimal(str(round(lat, 6))),
                longitude=Decimal(str(round(lon, 6))),
                risk_score=Decimal(str(RNG.randint(0, 95))),
                outcome_label=RNG.choice(outcomes),
                result_payload=demo_meta(detection_source=RNG.choice(scan_types), city=city, state=state),
                metadata=demo_meta(),
                created_at=now - timedelta(hours=RNG.randint(1, 720)),
            )
        )
        if len(scan_buf) >= 400:
            ScanEvent.objects.bulk_create(scan_buf)
            scan_buf = []
    if scan_buf:
        ScanEvent.objects.bulk_create(scan_buf)
    counts["scans"] = scale["scans"]

    mult = scale["event_multiplier"]
    alerts_n = signals_n = 0
    sev_map = {"medium": "warning", "high": "warning", "critical": "critical", "warning": "warning"}

    for cat_key, signal_type, full_count, severity in EVENT_CATEGORIES:
        count = max(1, int(full_count * mult)) if lite else full_count
        alert_sev = sev_map.get(severity, "warning")
        for n in range(count):
            org = RNG.choice(pharmacies + manufacturers + orgs_by_type.get("distributor", []))
            product = RNG.choice(products) if products else None
            state, city, lat, lon = _loc(n + alerts_n)
            officer = RNG.choice(staff) if staff else None
            detected = now - timedelta(hours=RNG.randint(2, 720))
            payload = demo_meta(
                category=cat_key,
                organisation_name=org.legal_name,
                organisation_type=org.organisation_type.code,
                address=org.address_line_1,
                state=state,
                city=city,
                phone=org.phone_number,
                contact_person=(org.metadata or {}).get("contact_person", "Duty officer"),
                product=product.name if product else "",
                batch=f"DEMO-B-{RNG.randint(1, 99):03d}",
                serial=f"NG-DEMO-{RNG.randint(100000, 999999)}",
                detected_at=detected.isoformat(),
                detection_source=signal_type,
                latitude=float(lat),
                longitude=float(lon),
                risk_score=RNG.randint(40, 98),
                confidence_score=RNG.randint(55, 95),
                recommended_action=RNG.choice(
                    ["Field inspection", "Recall verification", "Custody audit", "Enforcement referral"]
                ),
                assigned_officer=officer.get_full_name() if officer else "",
                assigned_officer_id=str(officer.pk) if officer else "",
                action_status=RNG.choice(["open", "in_progress", "pending_review"]),
                escalation_status=RNG.choice(["none", "escalated", "watch"]),
            )
            NationalAlert.objects.create(
                alert_type=cat_key,
                title=f"{cat_key.replace('_', ' ').title()} — {org.trading_name or org.legal_name}",
                description=f"Operational demo event in {city}, {state}",
                severity=alert_sev,
                organisation=org,
                product=product,
                state=state,
                risk_score=Decimal(str(payload["risk_score"])),
                evidence_payload=payload,
                metadata=demo_meta(category=cat_key),
                created_at=detected,
            )
            alerts_n += 1
            IntelligenceSignal.objects.create(
                signal_type=signal_type,
                organisation=org,
                product=product,
                region_state=state,
                severity=alert_sev,
                confidence=Decimal(str(payload["confidence_score"])),
                title=f"Signal: {cat_key} ({city})",
                summary=f"Demo intelligence signal for {product.name if product else 'national'} in {state}",
                evidence=payload,
                metadata=demo_meta(category=cat_key),
                is_active=True,
                created_at=detected,
            )
            signals_n += 1
    counts["alerts"] = alerts_n
    counts["signals"] = signals_n

    for i in range(max(3, int(12 * mult))):
        org = RNG.choice(pharmacies)
        state, _, _, _ = _loc(i)
        CounterfeitCluster.objects.get_or_create(
            cluster_code=f"DEMO-CLU-{state[:3].upper()}-{i + 1:03d}",
            defaults={
                "product": RNG.choice(products) if products else None,
                "region_state": state,
                "scan_count": RNG.randint(20, 200),
                "suspicious_count": RNG.randint(5, 80),
                "confidence": Decimal(str(RNG.randint(60, 95))),
                "status": "open",
                "metadata": demo_meta(),
            },
        )

    case_ids = []
    for i in range(max(5, int(25 * mult))):
        case = create_enforcement_case(
            title=f"Demo investigation {i + 1}",
            summary="National operational demo enforcement case",
            severity=RNG.choice(["low", "medium", "high", "critical"]),
            organisation=RNG.choice(pharmacies) if pharmacies else None,
            actor=RNG.choice(staff) if staff else None,
        )
        case.metadata = demo_meta()
        case.save(update_fields=["metadata", "updated_at"])
        case_ids.append(case.id)
    counts["enforcement_cases"] = len(case_ids)

    NationalRiskSnapshot.objects.create(
        national_score=Decimal("62.5"),
        status="amber",
        confidence=Decimal("78"),
        reasons=["Elevated counterfeit signals", "Regional shortage pressure", "Customs holds"],
        recommended_actions=["Prioritise Lagos-Kano corridor inspections", "Activate recall desk"],
        metrics=demo_meta(seed="20a2"),
        metadata=demo_meta(),
    )
    counts["risk_snapshots"] = 1

    return {"status": "seeded", "demo_type": DEMO_TYPE, "lite": lite, "counts": counts}
