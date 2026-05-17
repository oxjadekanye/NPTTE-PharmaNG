from django.urls import path

from apps.national_analytics.api.views import (
    HeatmapsView,
    MedicineFlowView,
    NationalSummaryView,
    RiskAnalysisView,
    StateComparisonView,
)

urlpatterns = [
    path("national-summary/", NationalSummaryView.as_view(), name="analytics-national-summary"),
    path("heatmaps/", HeatmapsView.as_view(), name="analytics-heatmaps"),
    path("medicine-flow/", MedicineFlowView.as_view(), name="analytics-medicine-flow"),
    path("risk-analysis/", RiskAnalysisView.as_view(), name="analytics-risk-analysis"),
    path("state-comparison/", StateComparisonView.as_view(), name="analytics-state-comparison"),
]
