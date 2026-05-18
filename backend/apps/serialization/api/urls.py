from django.urls import path

from apps.serialization.api.views import (
    SerializationDashboardView,
    SerializationDecodeScanView,
    SerializationLabelView,
    SerializationPackagingCreateView,
    SerializationScanHistoryView,
)

urlpatterns = [
    path("dashboard/", SerializationDashboardView.as_view(), name="serialization-dashboard"),
    path("decode/", SerializationDecodeScanView.as_view(), name="serialization-decode"),
    path("labels/<uuid:serial_id>/", SerializationLabelView.as_view(), name="serialization-label"),
    path("packaging/", SerializationPackagingCreateView.as_view(), name="serialization-packaging"),
    path("scan-history/", SerializationScanHistoryView.as_view(), name="serialization-scan-history"),
]
