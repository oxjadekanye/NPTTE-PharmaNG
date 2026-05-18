from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.command_center.incident_workflow import assign_investigator, escalate_incident
from apps.command_center.models import NationalIncident
from apps.core.api.responses import api_response
from apps.core.permissions import IsRegulatorUser


class IncidentAssignView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def post(self, request):
        incident = NationalIncident.objects.get(incident_code=request.data["incident_code"])
        incident = assign_investigator(
            incident=incident,
            investigator=request.data["investigator"],
            actor=request.user,
        )
        return api_response(
            data={"incident_code": incident.incident_code, "assigned": incident.assigned_investigator},
            message="Investigator assigned",
        )


class IncidentEscalateView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def post(self, request):
        incident = NationalIncident.objects.get(incident_code=request.data["incident_code"])
        incident = escalate_incident(
            incident=incident,
            reason=request.data.get("reason", "Operational escalation"),
            national=request.data.get("national", False),
        )
        return api_response(
            data={"incident_code": incident.incident_code, "escalation_level": incident.escalation_level},
            message="Incident escalated",
        )
