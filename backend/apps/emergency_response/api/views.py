from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.permissions import IsRegulatorUser
from apps.emergency_response.models import NationalEmergencyProtocol
from apps.emergency_response.services import activate_emergency_distribution_mode


class EmergencyProtocolListView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        protocols = NationalEmergencyProtocol.objects.filter(is_active=True).order_by("-activated_at")[:20]
        return api_response(
            data={
                "protocols": [
                    {"code": p.protocol_code, "title": p.title, "mode": p.mode} for p in protocols
                ]
            }
        )


class ActivateEmergencyView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def post(self, request):
        code = request.data.get("protocol_code", "NATIONAL-CRISIS")
        title = request.data.get("title", "National emergency distribution")
        states = request.data.get("target_states", [])
        protocol = activate_emergency_distribution_mode(
            protocol_code=code, title=title, actor=request.user, target_states=states
        )
        return api_response(data={"protocol_code": protocol.protocol_code, "mode": protocol.mode})
