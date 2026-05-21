from django.urls import path

from apps.pharmacies.api.inventory_ops_views import PharmacyInventorySyncView, PharmacyStockMovementView
from apps.pharmacies.api.views import (
    PharmacyAvailabilityView,
    PharmacyInventoryDetailView,
    PharmacyInventoryListCreateView,
    PharmacyProfileView,
    PharmacyTraceabilityDispenseView,
    PharmacyTraceabilityReceiveView,
)

urlpatterns = [
    path("profile/", PharmacyProfileView.as_view(), name="pharmacy-profile"),
    path("inventory/", PharmacyInventoryListCreateView.as_view(), name="pharmacy-inventory-list"),
    path(
        "inventory/<uuid:pk>/",
        PharmacyInventoryDetailView.as_view(),
        name="pharmacy-inventory-detail",
    ),
    path("availability/", PharmacyAvailabilityView.as_view(), name="pharmacy-availability"),
    path("inventory/movement/", PharmacyStockMovementView.as_view(), name="pharmacy-inventory-movement"),
    path("inventory/sync/", PharmacyInventorySyncView.as_view(), name="pharmacy-inventory-sync"),
    path("traceability/receive-batch/", PharmacyTraceabilityReceiveView.as_view(), name="pharmacy-trace-receive"),
    path("traceability/dispense-serial/", PharmacyTraceabilityDispenseView.as_view(), name="pharmacy-trace-dispense"),
]
