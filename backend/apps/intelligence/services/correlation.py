"""Event correlation engine — deterministic rules and thresholds."""
from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import timedelta

from django.utils import timezone

from apps.intelligence.models import CounterfeitCluster, IntelligenceSignal
from apps.intelligence.services.events import publish_intelligence_event
from apps.organisations.models import Organisation
from apps.products.models import Product
from apps.scanning.models import ScanEvent


def run_correlation(*, window_hours: int = 24, suspicious_threshold: int = 3) -> dict:
    since = timezone.now() - timedelta(hours=window_hours)
    suspicious_scans = ScanEvent.objects.filter(created_at__gte=since).filter(
        outcome_label__icontains="suspicious"
    )
    signals_created = []
    clusters_created = []

    by_product: dict[str, list] = defaultdict(list)
    by_region: dict[str, list] = defaultdict(list)
    for scan in suspicious_scans[:500]:
        key = scan.serial_number[:20] if scan.serial_number else "unknown"
        by_product[key].append(scan)
        region = ""
        if scan.organisation_id:
            region = Organisation.objects.filter(pk=scan.organisation_id).values_list("state", flat=True).first() or ""
        if region:
            by_region[region].append(scan)

    for region, scans in by_region.items():
        if len(scans) >= suspicious_threshold:
            sig = IntelligenceSignal.objects.create(
                signal_type=IntelligenceSignal.SIGNAL_CLUSTER,
                region_state=region,
                severity="high" if len(scans) >= 5 else "medium",
                confidence=min(95, 50 + len(scans) * 5),
                title=f"Regional scan cluster: {region}",
                summary=f"{len(scans)} suspicious scans in {window_hours}h window",
                evidence={"scan_count": len(scans), "region": region},
                organisation=scans[0].organisation if scans else None,
            )
            signals_created.append(str(sig.id))
            publish_intelligence_event("intelligence.signal.created", {"signal_id": str(sig.id), "region": region})

    for product_key, scans in by_product.items():
        if len(scans) >= suspicious_threshold:
            product = Product.objects.filter(name__icontains=product_key[:8]).first() if len(product_key) > 3 else None
            cluster_code = f"CC-{uuid.uuid4().hex[:8].upper()}"
            region = ""
            if scans[0].organisation_id:
                org = Organisation.objects.filter(pk=scans[0].organisation_id).first()
                region = org.state if org else ""
            cluster = CounterfeitCluster.objects.create(
                cluster_code=cluster_code,
                product=product,
                region_state=region,
                scan_count=len(scans),
                suspicious_count=len(scans),
                confidence=min(95, 55 + len(scans) * 4),
                serial_numbers=[s.serial_number for s in scans[:20]],
            )
            clusters_created.append(cluster_code)
            publish_intelligence_event(
                "intelligence.cluster.detected",
                {"cluster_code": cluster_code, "scan_count": len(scans)},
            )

    duplicate_count = ScanEvent.objects.filter(created_at__gte=since, outcome_label__icontains="duplicate").count()
    if duplicate_count >= suspicious_threshold:
        sig = IntelligenceSignal.objects.create(
            signal_type=IntelligenceSignal.SIGNAL_DUPLICATE,
            severity="medium",
            confidence=70,
            title="Duplicate scan cluster detected",
            summary=f"{duplicate_count} duplicate scans in {window_hours}h",
            evidence={"duplicate_count": duplicate_count},
        )
        signals_created.append(str(sig.id))

    return {
        "signals_created": len(signals_created),
        "clusters_created": len(clusters_created),
        "signal_ids": signals_created,
        "cluster_codes": clusters_created,
    }
