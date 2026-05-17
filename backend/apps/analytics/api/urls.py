from django.urls import path

from apps.analytics.api.views import (
    NationalInventorySummaryView,
    StateBreakdownView,
    TopProductsView,
    TransactionVolumeView,
)

from apps.national_analytics.api.views import (
    HeatmapsView,
    MedicineFlowView,
    NationalSummaryView,
    RiskAnalysisView,
    StateComparisonView,
)

urlpatterns = [
    path("inventory/summary/", NationalInventorySummaryView.as_view()),
    path("transactions/volume/", TransactionVolumeView.as_view()),
    path("inventory/by-state/", StateBreakdownView.as_view()),
    path("products/top/", TopProductsView.as_view()),
    # Phase 5 — national analytics engine (additive)
    path("national-summary/", NationalSummaryView.as_view(), name="analytics-national-summary"),
    path("heatmaps/", HeatmapsView.as_view(), name="analytics-heatmaps"),
    path("medicine-flow/", MedicineFlowView.as_view(), name="analytics-medicine-flow"),
    path("risk-analysis/", RiskAnalysisView.as_view(), name="analytics-risk-analysis"),
    path("state-comparison/", StateComparisonView.as_view(), name="analytics-state-comparison"),
]
