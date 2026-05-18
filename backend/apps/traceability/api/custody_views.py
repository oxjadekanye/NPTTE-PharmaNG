from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.permissions import IsRegulatorUser
from apps.serialization.models import ProductSerial
from apps.organisations.models import Organisation
from apps.traceability.custody_services import custody_timeline_for_serial, record_custody_transfer
from apps.traceability.recall_execution import (
    acknowledge_pharmacy_recall,
    acknowledge_warehouse_recall,
    launch_recall_campaign,
)
from apps.traceability.models import BatchRecall, RecallExecutionCampaign
from apps.tenancy.services.tenant import get_active_organisation_id, user_can_access_organisation


class CustodyTimelineView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        serial_number = request.query_params.get("serial_number")
        if not serial_number:
            return api_response(data={"timeline": []}, message="serial_number required", status_code=400)
        product_serial = ProductSerial.objects.get(serial_number=serial_number)
        timeline = custody_timeline_for_serial(product_serial=product_serial)
        return api_response(data={"serial_number": serial_number, "timeline": timeline}, message="Custody timeline")


class CustodyRecordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serial_number = request.data.get("serial_number")
        product_serial = ProductSerial.objects.get(serial_number=serial_number)
        dest_org = None
        dest_id = request.data.get("destination_organisation_id")
        if dest_id:
            dest_org = Organisation.objects.filter(pk=dest_id).first()
        event = record_custody_transfer(
            product_serial=product_serial,
            source_node=request.data.get("source_node", ""),
            destination_node=request.data["destination_node"],
            destination_organisation=dest_org,
            latitude=request.data.get("latitude"),
            longitude=request.data.get("longitude"),
            actor=request.user,
            confirm=request.data.get("confirm", False),
        )
        return api_response(
            data={"event_id": str(event.id), "integrity_status": event.integrity_status},
            message="Custody transfer recorded",
            status_code=201,
        )


class RecallExecutionListView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        campaigns = RecallExecutionCampaign.objects.select_related("batch_recall").order_by("-created_at")[:50]
        rows = [
            {
                "campaign_code": c.campaign_code,
                "status": c.status,
                "pharmacies_targeted": c.pharmacies_targeted,
                "pharmacies_acknowledged": c.pharmacies_acknowledged,
                "estimated_patient_exposure": c.estimated_patient_exposure,
                "quarantine_active": c.quarantine_active,
            }
            for c in campaigns
        ]
        return api_response(data={"campaigns": rows}, message="Recall execution campaigns")


class RecallExecutionLaunchView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def post(self, request):
        recall = BatchRecall.objects.get(pk=request.data["batch_recall_id"])
        campaign = launch_recall_campaign(
            batch_recall=recall,
            pharmacies_targeted=int(request.data.get("pharmacies_targeted", 0)),
            actor=request.user,
        )
        return api_response(
            data={"campaign_code": campaign.campaign_code},
            message="Recall campaign launched",
            status_code=201,
        )


class RecallPharmacyAcknowledgeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        campaign = RecallExecutionCampaign.objects.get(pk=request.data["campaign_id"])
        org_id = request.data.get("organisation_id") or get_active_organisation_id(request)
        pharmacy = Organisation.objects.get(pk=org_id)
        if not user_can_access_organisation(request.user, pharmacy.id):
            return api_response(message="Access denied", status_code=403)
        completion_pct = int(request.data.get("completion_pct", 100))
        ack = acknowledge_pharmacy_recall(
            campaign=campaign,
            pharmacy_organisation=pharmacy,
            completion_pct=completion_pct,
        )
        from apps.operations.services.recall_ops import on_recall_acknowledged

        on_recall_acknowledged(campaign=campaign, organisation=pharmacy, actor=request.user, ack_type="pharmacy")
        return api_response(
            data={"acknowledged_at": ack.acknowledged_at.isoformat(), "completion_pct": ack.completion_pct},
            message="Pharmacy recall acknowledged",
            status_code=201,
        )


class RecallWarehouseAcknowledgeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        campaign = RecallExecutionCampaign.objects.get(pk=request.data["campaign_id"])
        org_id = request.data.get("organisation_id") or get_active_organisation_id(request)
        warehouse = Organisation.objects.get(pk=org_id)
        if not user_can_access_organisation(request.user, warehouse.id):
            return api_response(message="Access denied", status_code=403)
        ack = acknowledge_warehouse_recall(
            campaign=campaign,
            warehouse_organisation=warehouse,
            completion_pct=int(request.data.get("completion_pct", 100)),
            escalation_required=bool(request.data.get("escalation_required", False)),
        )
        from apps.operations.services.recall_ops import on_recall_acknowledged

        on_recall_acknowledged(campaign=campaign, organisation=warehouse, actor=request.user, ack_type="warehouse")
        return api_response(
            data={
                "acknowledged_at": ack.acknowledged_at.isoformat(),
                "completion_pct": ack.completion_pct,
                "escalation_required": ack.escalation_required,
            },
            message="Warehouse recall acknowledged",
            status_code=201,
        )
