"""Phase 12 — supply chain & recall orchestration APIs."""
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.permissions import IsRegulatorUser
from apps.traceability.models import RecallExecutionCampaign
from apps.traceability.supply_chain_intelligence import (
    custody_transfer_audit,
    customs_clearance_stages,
    shipment_timeline,
)


class SupplyChainShipmentTimelineView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        tracking = request.GET.get("tracking_number")
        rows = shipment_timeline(tracking_number=tracking, limit=int(request.GET.get("limit", 30)))
        return api_response(
            data={"shipments": rows, "custody_audit": custody_transfer_audit(limit=20), "count": len(rows)},
            message="Supply chain shipment timeline",
        )


class SupplyChainCustodyExplorerView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        return api_response(
            data={
                "transfers": custody_transfer_audit(limit=int(request.GET.get("limit", 50))),
                "customs_stages": customs_clearance_stages(),
            },
            message="Custody explorer",
        )


class RecallOrchestrationCenterView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        campaigns = RecallExecutionCampaign.objects.select_related("batch_recall").order_by("-created_at")[:30]
        rows = [
            {
                "id": str(c.id),
                "campaign_code": c.campaign_code,
                "status": c.status,
                "pharmacies_targeted": c.pharmacies_targeted,
                "pharmacies_acknowledged": c.pharmacies_acknowledged,
                "estimated_patient_exposure": c.estimated_patient_exposure,
                "batch_recall_id": str(c.batch_recall_id) if c.batch_recall_id else None,
                "created_at": c.created_at.isoformat(),
            }
            for c in campaigns
        ]
        completion = sum(1 for c in campaigns if c.pharmacies_acknowledged >= c.pharmacies_targeted) if campaigns else 0
        return api_response(
            data={
                "campaigns": rows,
                "active_count": sum(1 for c in campaigns if c.status == "active"),
                "completion_metrics": {"fully_acknowledged": completion, "total": len(rows)},
            },
            message="Recall orchestration center",
        )
