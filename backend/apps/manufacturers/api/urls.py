from django.urls import path

from apps.manufacturers.api.views import (
    BatchCreateView,
    BatchListView,
    ManufacturerProfileView,
    ManufacturingSiteListView,
    RecallNoticeCreateView,
)

urlpatterns = [
    path("profile/", ManufacturerProfileView.as_view(), name="manufacturer-profile"),
    path("sites/", ManufacturingSiteListView.as_view(), name="manufacturer-sites"),
    path("batches/", BatchListView.as_view(), name="manufacturer-batches"),
    path("batches/create/", BatchCreateView.as_view(), name="manufacturer-batch-create"),
    path("recalls/", RecallNoticeCreateView.as_view(), name="manufacturer-recalls"),
]
