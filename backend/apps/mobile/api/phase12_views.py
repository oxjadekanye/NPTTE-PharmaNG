"""Phase 12 — national field operations workflows."""
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.roles import is_regulator_user
from apps.mobile.services.mobile_audit import record_mobile_audit
from apps.operations.services.task_engine import create_operational_task, escalate_task, serialize_task
from apps.organisations.models import Organisation


class RegulatorSeizureWorkflowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not is_regulator_user(request.user) and not request.user.is_superuser:
            return api_response(message="Regulator access required", status_code=403)
        org = Organisation.objects.filter(pk=request.user.organisation_id).first() if request.user.organisation_id else None
        task = create_operational_task(
            title=request.data.get("title", "Field seizure"),
            task_type="enforcement_seizure",
            organisation=org,
            assigned_to=request.user,
            description=request.data.get("notes", ""),
            priority="high",
            created_by=request.user,
        )
        if request.data.get("escalate"):
            escalate_task(task=task, actor=request.user, reason="Mobile seizure escalation")
        record_mobile_audit(request=request, action_type="regulator.seizure", payload={"task_id": str(task.id)})
        return api_response(data={"task": serialize_task(task)}, message="Seizure workflow recorded", status_code=201)


class CustomsShipmentHoldView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        record_mobile_audit(
            request=request,
            action_type="customs.shipment_hold",
            payload={
                "tracking_number": request.data.get("tracking_number"),
                "reason": request.data.get("reason", ""),
            },
        )
        return api_response(
            data={"status": "hold_recorded", "tracking_number": request.data.get("tracking_number")},
            message="Shipment hold workflow",
            status_code=201,
        )


class WarehouseTransferConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        record_mobile_audit(
            request=request,
            action_type="warehouse.transfer_confirm",
            payload=request.data,
        )
        return api_response(data={"confirmed": True}, message="Transfer confirmed", status_code=201)


class PharmacyRecallAckWorkflowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        record_mobile_audit(request=request, action_type="pharmacy.recall_ack", payload=request.data)
        return api_response(data={"acknowledged": True}, message="Recall acknowledgement recorded", status_code=201)
