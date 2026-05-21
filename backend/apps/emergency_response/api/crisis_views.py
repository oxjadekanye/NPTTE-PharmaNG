"""Phase 12 — executive crisis mode API."""
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.constants import EmergencyMode
from apps.core.permissions import IsRegulatorUser
from apps.emergency_response.models import NationalEmergencyProtocol
from apps.emergency_response.services import activate_emergency_distribution_mode
from apps.streambus.services.bus import publish_operational_event


CRISIS_SCENARIOS = {
    "counterfeit_outbreak": "Counterfeit outbreak — national verification surge",
    "medicine_shortage": "Medicine shortage crisis — strategic allocation",
    "border_seizure": "Border seizure event — customs hold coordination",
    "emergency_recall": "Emergency recall — multi-channel propagation",
    "contamination_alert": "National contamination alert — quarantine protocol",
}


class CrisisModeStatusView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        active = NationalEmergencyProtocol.objects.filter(mode=EmergencyMode.CRISIS).order_by("-activated_at").first()
        return api_response(
            data={
                "active": bool(active),
                "protocol_code": active.protocol_code if active else None,
                "title": active.title if active else None,
                "scenarios": list(CRISIS_SCENARIOS.keys()),
                "readiness_shift": "elevated" if active else "normal",
            },
            message="Crisis mode status",
        )


class CrisisModeActivateView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def post(self, request):
        scenario = request.data.get("scenario", "counterfeit_outbreak")
        title = CRISIS_SCENARIOS.get(scenario, "National crisis activation")
        states = request.data.get("target_states", [])
        protocol = activate_emergency_distribution_mode(
            protocol_code=f"CRISIS-{scenario[:12].upper()}",
            title=title,
            actor=request.user,
            target_states=states,
        )
        publish_operational_event(
            event_type="crisis.activated",
            payload={"scenario": scenario, "title": title},
            severity="CRITICAL",
        )
        return api_response(
            data={
                "scenario": scenario,
                "protocol_code": protocol.protocol_code,
                "mode": protocol.mode,
                "executive_broadcast": f"National directive: {title}",
                "timeline": [
                    {"step": "activation", "at": protocol.activated_at.isoformat() if protocol.activated_at else None},
                    {"step": "operational_readiness", "status": "shifted"},
                ],
            },
            message="Crisis mode activated",
            status_code=201,
        )
