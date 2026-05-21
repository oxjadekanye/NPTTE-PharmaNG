"""Phase 12 — pharmacy network intelligence API."""
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.permissions import IsRegulatorUser
from apps.pharmacies.pharmacy_network import nearest_verified_pharmacies, pharmacy_network_ranking


class PharmacyNetworkRankingView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        rows = pharmacy_network_ranking(limit=int(request.GET.get("limit", 30)))
        return api_response(data={"pharmacies": rows, "count": len(rows)}, message="Pharmacy network ranking")


class NearestVerifiedPharmaciesView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        state = request.GET.get("state", "")
        rows = nearest_verified_pharmacies(state=state)
        return api_response(data={"pharmacies": rows}, message="Nearest verified pharmacies")
