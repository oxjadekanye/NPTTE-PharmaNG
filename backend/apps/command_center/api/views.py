from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.command_center.services import NationalCommandService
from apps.core.api.responses import api_response
from apps.core.permissions import IsRegulatorUser
from apps.core.throttling import CommandCenterThrottle


class _CommandCenterView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]
    throttle_classes = [CommandCenterThrottle]
    service_method = ""

    def get(self, request):
        data = getattr(NationalCommandService, self.service_method)()
        return api_response(data=data)


class LiveOverviewView(_CommandCenterView):
    service_method = "live_overview"


class ThreatMapView(_CommandCenterView):
    service_method = "threat_map"


class ActiveIncidentsView(_CommandCenterView):
    service_method = "active_incidents"


class EmergencyResponseView(_CommandCenterView):
    service_method = "emergency_response"


class RegionalRiskView(_CommandCenterView):
    service_method = "regional_risk"
