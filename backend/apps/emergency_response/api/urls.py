from django.urls import path

from apps.emergency_response.api.crisis_views import CrisisModeActivateView, CrisisModeStatusView
from apps.emergency_response.api.views import ActivateEmergencyView, EmergencyProtocolListView

urlpatterns = [
    path("protocols/", EmergencyProtocolListView.as_view(), name="emergency-protocols"),
    path("activate/", ActivateEmergencyView.as_view(), name="emergency-activate"),
    path("crisis-mode/", CrisisModeStatusView.as_view(), name="crisis-mode-status"),
    path("crisis-mode/activate/", CrisisModeActivateView.as_view(), name="crisis-mode-activate"),
]
