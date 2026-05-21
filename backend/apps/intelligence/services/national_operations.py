"""Phase 11 — national executive operational metrics (seeded/demo-safe)."""
from __future__ import annotations

from django.db.models import Q
from django.utils import timezone

from apps.alerts.models import NationalAlert
from apps.core.constants import AvailabilityStatus
from apps.inventory.models import InventoryItem
from apps.operations.models import OperationalTask
from apps.scanning.models import ScanEvent


def build_national_operations_metrics() -> dict:
    """Deterministic national KPIs from operational data + safe demo fallbacks."""
    now = timezone.now()
    open_tasks = OperationalTask.objects.filter(
        task_status__in=(OperationalTask.STATUS_OPEN, OperationalTask.STATUS_IN_PROGRESS)
    ).count()
    overdue = OperationalTask.objects.filter(
        task_status__in=(OperationalTask.STATUS_OPEN, OperationalTask.STATUS_IN_PROGRESS),
        due_at__lt=now,
    ).count()
    low_stock = InventoryItem.objects.filter(
        Q(availability_status=AvailabilityStatus.LOW_STOCK) | Q(quantity_on_hand__lte=10)
    ).count()
    recall_alerts = NationalAlert.objects.filter(alert_type__icontains="recall").count()
    suspicious_scans = ScanEvent.objects.filter(outcome_label__icontains="suspicious").count()
    total_scans = max(ScanEvent.objects.count(), 1)

    counterfeit_heat = min(100, int(35 + (suspicious_scans / total_scans) * 65))
    shortage_index = min(100, int(20 + low_stock * 2 + recall_alerts * 3))
    readiness = max(0, 100 - overdue * 2 - int(shortage_index * 0.3))

    states = [
        {"state": "Lagos", "compliance_score": 78, "open_incidents": 12},
        {"state": "Kano", "compliance_score": 71, "open_incidents": 8},
        {"state": "Rivers", "compliance_score": 82, "open_incidents": 5},
        {"state": "FCT", "compliance_score": 88, "open_incidents": 3},
    ]

    return {
        "medicine_shortage_index": shortage_index,
        "counterfeit_risk_heat_score": counterfeit_heat,
        "national_operational_readiness_score": readiness,
        "import_dependency_index": 62,
        "border_threat_score": min(100, 40 + suspicious_scans),
        "emergency_medicine_readiness": max(0, readiness - 5),
        "state_compliance": states,
        "pharmacy_compliance_ranking": [
            {"rank": 1, "name": "Demo Pharmacy Lagos Central", "score": 94},
            {"rank": 2, "name": "Demo Pharmacy Abuja North", "score": 91},
            {"rank": 3, "name": "Demo Pharmacy PH East", "score": 87},
        ],
        "open_operational_tasks": open_tasks,
        "overdue_tasks": overdue,
        "active_recall_alerts": recall_alerts,
        "low_stock_skus": low_stock,
        "computed_at": now.isoformat(),
        "disclaimer": "Demo operational metrics — not live pharmacy connectivity.",
    }
