"""
NPTTE API v1 URL configuration.
"""
from django.urls import include, path

from apps.core.api.views import HealthCheckView

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="api-health"),
    path("auth/", include("apps.accounts.api.urls")),
    path("pharmacies/", include("apps.pharmacies.api.urls")),
    path("patients/", include("apps.patients.api.urls")),
]
