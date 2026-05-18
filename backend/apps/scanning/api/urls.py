from django.urls import path

from apps.scanning.api.views import ScanHistoryView, ScanIngestView, ScanSyncPendingView

urlpatterns = [
    path("ingest/", ScanIngestView.as_view(), name="scanning-ingest"),
    path("history/", ScanHistoryView.as_view(), name="scanning-history"),
    path("sync-pending/", ScanSyncPendingView.as_view(), name="scanning-sync-pending"),
]
