from django.urls import path

from apps.national_dashboard.api.views import (
    CounterfeitMapView,
    HighRiskOrganisationsView,
    NationalOverviewDashboardView,
    ShortagesDashboardView,
    StateAnalyticsView,
    SupplyChainDashboardView,
    VerificationTrafficView,
)

urlpatterns = [
    path("overview/", NationalOverviewDashboardView.as_view(), name="dashboard-overview"),
    path("national-overview/", NationalOverviewDashboardView.as_view(), name="dashboard-national-overview"),
    path("counterfeit-map/", CounterfeitMapView.as_view(), name="dashboard-counterfeit-map"),
    path("shortages/", ShortagesDashboardView.as_view(), name="dashboard-shortages"),
    path("supply-chain/", SupplyChainDashboardView.as_view(), name="dashboard-supply-chain"),
    path(
        "high-risk-organisations/",
        HighRiskOrganisationsView.as_view(),
        name="dashboard-high-risk-orgs",
    ),
    path("verification-traffic/", VerificationTrafficView.as_view(), name="dashboard-verify-traffic"),
    path("state-analytics/", StateAnalyticsView.as_view(), name="dashboard-state-analytics"),
]
