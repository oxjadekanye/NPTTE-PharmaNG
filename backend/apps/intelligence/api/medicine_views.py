"""Phase 12 — medicine & manufacturer intelligence APIs."""
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.permissions import IsRegulatorUser
from apps.fraud_detection.counterfeit_engine import analyze_counterfeit_national
from apps.intelligence.services.medicine_intelligence import (
    get_medicine_intelligence,
    list_manufacturer_intelligence,
    list_medicine_intelligence,
    national_counterfeit_risk,
    national_shortage_risk,
)


class MedicineIntelligenceListView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        q = request.GET.get("q", "")
        limit = int(request.GET.get("limit", 50))
        rows = list_medicine_intelligence(query=q, limit=limit)
        return api_response(data={"medicines": rows, "count": len(rows)}, message="Medicine intelligence")


class MedicineIntelligenceDetailView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request, pk):
        profile = get_medicine_intelligence(pk)
        if not profile:
            return api_response(message="Medicine not found", status_code=404)
        return api_response(data=profile, message="Medicine intelligence profile")


class ManufacturerIntelligenceListView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        rows = list_manufacturer_intelligence(limit=int(request.GET.get("limit", 30)))
        return api_response(data={"manufacturers": rows, "count": len(rows)}, message="Manufacturer intelligence")


class ShortageRiskView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        return api_response(data=national_shortage_risk(), message="National shortage risk")


class CounterfeitRiskView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        summary = national_counterfeit_risk()
        analysis = analyze_counterfeit_national(window_hours=int(request.GET.get("window_hours", 168)))
        return api_response(
            data={"summary": summary, "analysis": analysis},
            message="National counterfeit risk",
        )
