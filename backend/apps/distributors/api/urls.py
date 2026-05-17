from django.urls import path

from apps.distributors.api.views import (
    DistributorProfileView,
    WarehouseDetailView,
    WarehouseListCreateView,
)

urlpatterns = [
    path("profile/", DistributorProfileView.as_view(), name="distributor-profile"),
    path("warehouses/", WarehouseListCreateView.as_view(), name="distributor-warehouses"),
    path("warehouses/<uuid:pk>/", WarehouseDetailView.as_view(), name="distributor-warehouse-detail"),
]
