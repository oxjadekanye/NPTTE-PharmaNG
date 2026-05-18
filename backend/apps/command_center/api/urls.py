from django.urls import path

from apps.command_center.api.incident_workflow_views import IncidentAssignView, IncidentEscalateView
from apps.command_center.api.views import (
    ActiveIncidentsView,
    EmergencyResponseView,
    LiveOverviewView,
    RegionalRiskView,
    ThreatMapView,
)

urlpatterns = [
    path("live-overview/", LiveOverviewView.as_view(), name="command-live-overview"),
    path("threat-map/", ThreatMapView.as_view(), name="command-threat-map"),
    path("active-incidents/", ActiveIncidentsView.as_view(), name="command-active-incidents"),
    path("emergency-response/", EmergencyResponseView.as_view(), name="command-emergency-response"),
    path("regional-risk/", RegionalRiskView.as_view(), name="command-regional-risk"),
    path("incidents/assign/", IncidentAssignView.as_view(), name="command-incident-assign"),
    path("incidents/escalate/", IncidentEscalateView.as_view(), name="command-incident-escalate"),
]
