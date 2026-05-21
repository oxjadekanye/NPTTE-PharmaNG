"""Phase 11 — mobile evidence timeline and field inspection workflow."""
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.roles import is_regulator_user
from apps.mobile.models import MobileFieldEvidence
from apps.mobile.services.mobile_audit import record_mobile_audit
from apps.operations.services.task_engine import create_operational_task, serialize_task


EVIDENCE_CATEGORIES = {
    "inspection": "Field inspection",
    "enforcement": "Enforcement seizure",
    "warehouse_breach": "Warehouse cold-chain breach",
    "customs_seizure": "Customs hold",
}


class MobileEvidenceTimelineView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = MobileFieldEvidence.objects.all().order_by("-created_at")
        if not is_regulator_user(request.user) and not request.user.is_superuser:
            qs = qs.filter(actor=request.user)
        limit = int(request.GET.get("limit", 50))
        rows = [
            {
                "id": str(e.id),
                "evidence_type": e.evidence_type,
                "category_label": EVIDENCE_CATEGORIES.get(e.evidence_type, e.evidence_type),
                "serial_number": e.serial_number,
                "notes": e.notes,
                "latitude": float(e.latitude) if e.latitude is not None else None,
                "longitude": float(e.longitude) if e.longitude is not None else None,
                "captured_at": e.created_at.isoformat(),
                "sync_status": e.sync_status,
                "photo_count": len(e.photos or []),
                "chain_of_custody": {
                    "actor": e.actor.username if e.actor else None,
                    "device_id": str(e.device_id) if e.device_id else None,
                },
            }
            for e in qs[:limit]
        ]
        return api_response(data={"timeline": rows, "count": len(rows)}, message="Evidence timeline")


class MobileInspectionWorkflowView(APIView):
    """Start or complete a guided field inspection (creates operational task)."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not is_regulator_user(request.user) and not request.user.is_superuser:
            return api_response(message="Regulator access required", status_code=403)
        action = request.data.get("action", "start")
        if action == "complete":
            record_mobile_audit(
                request=request,
                action_type="inspection.completed",
                payload=request.data,
            )
            return api_response(
                data={
                    "report": {
                        "status": "completed",
                        "violations": request.data.get("violations", []),
                        "checklist_score": request.data.get("checklist_score"),
                        "signature_note": request.data.get("signature_note", ""),
                    }
                },
                message="Inspection completed",
            )
        from apps.organisations.models import Organisation

        org = (
            Organisation.objects.filter(pk=request.user.organisation_id).first()
            if request.user.organisation_id
            else None
        )
        task = create_operational_task(
            title=request.data.get("title", "Field inspection"),
            task_type="field_inspection",
            organisation=org,
            assigned_to=request.user,
            description=request.data.get("description", ""),
            priority=request.data.get("priority", "normal"),
            related_entity_type="inspection",
            created_by=request.user,
        )
        record_mobile_audit(request=request, action_type="inspection.started", payload={"task_id": str(task.id)})
        return api_response(
            data={"task": serialize_task(task), "steps": ["site", "product", "compliance", "evidence", "sign-off"]},
            message="Inspection workflow started",
            status_code=201,
        )
