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
    path("analytics/", include("apps.analytics.api.urls")),  # includes national analytics (Phase 5)
    path("dashboard/", include("apps.national_dashboard.api.urls")),
    path("alerts/", include("apps.alerts.api.urls")),
    path("manufacturers/", include("apps.manufacturers.api.urls")),
    # Phase 5 — supply chain & clinical (additive)
    path("distributors/", include("apps.distributors.api.urls")),
    path("logistics/", include("apps.logistics.api.urls")),
    path("prescriptions/", include("apps.prescriptions.api.urls")),
    path("regulatory/", include("apps.regulatory.api.urls")),
    path("emergency/", include("apps.emergency.api.urls")),
    path("international/", include("apps.international.api.urls")),
    # Phase 5 — national command platform (additive)
    path("command-center/", include("apps.command_center.api.urls")),
    path("events/", include("apps.events.api.urls")),
    path("market-intelligence/", include("apps.market_intelligence.api.urls")),
    path("public/", include("apps.citizen.api.urls")),
    path("onboarding/", include("apps.onboarding.api.urls")),
    path("emergency-response/", include("apps.emergency_response.api.urls")),
    path("mobile/", include("apps.mobile.api.urls")),
    # Phase 6 — realtime SSE (additive)
    path("realtime/", include("apps.realtime.api.urls")),
]
