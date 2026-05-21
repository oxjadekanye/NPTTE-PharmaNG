from django.urls import path

from apps.ai_engine.api.views import NationalIntelligenceView, SerialRiskScoreView
from apps.intelligence.api.views import (
    CounterfeitClustersView,
    ExecutiveBriefingView,
    IntelligenceSignalsView,
    NarrativesView,
    NationalOperationsMetricsView,
    NationalRiskView,
    OrganisationRiskView,
    ProductRiskView,
    RegionalRiskView,
    RunCorrelationView,
)

urlpatterns = [
    path("national-risk/", NationalRiskView.as_view(), name="intelligence-national-risk"),
    path("regional-risk/", RegionalRiskView.as_view(), name="intelligence-regional-risk"),
    path("product-risk/", ProductRiskView.as_view(), name="intelligence-product-risk"),
    path("organisation-risk/", OrganisationRiskView.as_view(), name="intelligence-organisation-risk"),
    path("signals/", IntelligenceSignalsView.as_view(), name="intelligence-signals"),
    path("clusters/", CounterfeitClustersView.as_view(), name="intelligence-clusters"),
    path("run-correlation/", RunCorrelationView.as_view(), name="intelligence-run-correlation"),
    path("narratives/", NarrativesView.as_view(), name="intelligence-narratives"),
    path("executive-briefing/", ExecutiveBriefingView.as_view(), name="intelligence-executive-briefing"),
    path(
        "national-operations/",
        NationalOperationsMetricsView.as_view(),
        name="intelligence-national-operations",
    ),
    # Phase 10 legacy routes (preserved)
    path("national/", NationalIntelligenceView.as_view(), name="intelligence-national-legacy"),
    path("serial-risk/", SerialRiskScoreView.as_view(), name="intelligence-serial-risk-legacy"),
]
