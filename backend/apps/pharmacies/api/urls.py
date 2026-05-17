from django.urls import path

from apps.pharmacies.api.views import (
    PharmacyAvailabilityView,
    PharmacyInventoryDetailView,
    PharmacyInventoryListCreateView,
    PharmacyProfileView,
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
]
