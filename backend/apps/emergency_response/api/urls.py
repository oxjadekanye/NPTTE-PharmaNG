from django.urls import path

from apps.emergency_response.api.views import ActivateEmergencyView, EmergencyProtocolListView

urlpatterns = [
    path("protocols/", EmergencyProtocolListView.as_view(), name="emergency-protocols"),
    path("activate/", ActivateEmergencyView.as_view(), name="emergency-activate"),
]
