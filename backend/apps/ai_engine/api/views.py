from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.ai_engine.national_intelligence import build_national_intelligence_snapshot, score_serial_risk
from apps.core.api.responses import api_response
from apps.core.permissions import IsRegulatorUser


class NationalIntelligenceView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        return api_response(data=build_national_intelligence_snapshot(), message="National AI intelligence snapshot")


class SerialRiskScoreView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serial = request.query_params.get("serial_number", "")
        if not serial:
            return api_response(data={}, message="serial_number required", status_code=400)
        return api_response(data=score_serial_risk(serial_number=serial), message="Serial risk score")
