from django.urls import path

from apps.analytics.api.views import (
    NationalInventorySummaryView,
    StateBreakdownView,
    TopProductsView,
    TransactionVolumeView,
)

urlpatterns = [
    path("inventory/summary/", NationalInventorySummaryView.as_view()),
    path("transactions/volume/", TransactionVolumeView.as_view()),
    path("inventory/by-state/", StateBreakdownView.as_view()),
    path("products/top/", TopProductsView.as_view()),
]
