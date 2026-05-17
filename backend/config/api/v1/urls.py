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
    # Phase 3 — additive national modules (existing routes unchanged)
    path("traceability/", include("apps.traceability.api.urls")),
    path("verification/", include("apps.verification.api.urls")),
    path("audit/", include("apps.audit.api.urls")),
    path("analytics/", include("apps.analytics.api.urls")),
    path("dashboard/", include("apps.national_dashboard.api.urls")),
    path("alerts/", include("apps.alerts.api.urls")),
]
