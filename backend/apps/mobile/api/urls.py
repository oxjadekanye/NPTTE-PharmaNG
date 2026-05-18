from django.urls import path

from apps.mobile.api.views import DeviceListView, DeviceRegisterView, OfflineSyncView, ScanIngestView

urlpatterns = [
    path("devices/register/", DeviceRegisterView.as_view(), name="mobile-device-register"),
    path("devices/", DeviceListView.as_view(), name="mobile-device-list"),
    path("scans/ingest/", ScanIngestView.as_view(), name="mobile-scan-ingest"),
    path("scans/sync-offline/", OfflineSyncView.as_view(), name="mobile-offline-sync"),
]
