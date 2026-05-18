from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.permissions import IsRegulatorUser
from apps.serialization.models import ProductSerial
from apps.organisations.models import Organisation
from apps.traceability.custody_services import custody_timeline_for_serial, record_custody_transfer
from apps.traceability.recall_execution import acknowledge_pharmacy_recall, launch_recall_campaign
from apps.traceability.models import BatchRecall, RecallExecutionCampaign


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
