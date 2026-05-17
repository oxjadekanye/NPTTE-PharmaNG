from django.urls import path

from apps.logistics.api.views import (
    ShipmentCheckpointView,
    ShipmentDeliveryConfirmView,
    ShipmentDetailView,
    ShipmentListCreateView,
)

urlpatterns = [
    path("shipments/", ShipmentListCreateView.as_view(), name="logistics-shipments"),
    path("shipments/<uuid:pk>/", ShipmentDetailView.as_view(), name="logistics-shipment-detail"),
    path("shipments/<uuid:pk>/checkpoint/", ShipmentCheckpointView.as_view(), name="logistics-checkpoint"),
    path(
        "shipments/<uuid:pk>/confirm-delivery/",
        ShipmentDeliveryConfirmView.as_view(),
        name="logistics-confirm-delivery",
    ),
]
