from django.urls import path

from apps.mobile.api.phase11_views import MobileEvidenceTimelineView, MobileInspectionWorkflowView
from apps.mobile.api.phase12_views import (
    CustomsShipmentHoldView,
    PharmacyRecallAckWorkflowView,
    RegulatorSeizureWorkflowView,
    WarehouseTransferConfirmView,
)
from apps.mobile.api.views import (
    DeviceHeartbeatView,
    DeviceListView,
    DeviceRegisterView,
    DeviceTrustView,
    EvidenceSyncView,
    FieldEvidenceView,
    MobileAuditTimelineView,
    MobileCopilotView,
    MobileRealtimeFeedView,
    OfflineSyncView,
    ScanIngestView,
)

urlpatterns = [
    path("devices/register/", DeviceRegisterView.as_view(), name="mobile-device-register"),
    path("devices/trust/", DeviceTrustView.as_view(), name="mobile-device-trust"),
    path("devices/heartbeat/", DeviceHeartbeatView.as_view(), name="mobile-device-heartbeat"),
    path("devices/", DeviceListView.as_view(), name="mobile-device-list"),
    path("scans/ingest/", ScanIngestView.as_view(), name="mobile-scan-ingest"),
    path("scans/sync-offline/", OfflineSyncView.as_view(), name="mobile-offline-sync"),
    path("evidence/", FieldEvidenceView.as_view(), name="mobile-field-evidence"),
    path("evidence/sync/", EvidenceSyncView.as_view(), name="mobile-evidence-sync"),
    path("evidence/timeline/", MobileEvidenceTimelineView.as_view(), name="mobile-evidence-timeline"),
    path("inspection/workflow/", MobileInspectionWorkflowView.as_view(), name="mobile-inspection-workflow"),
    path("audit/timeline/", MobileAuditTimelineView.as_view(), name="mobile-audit-timeline"),
    path("realtime/feed/", MobileRealtimeFeedView.as_view(), name="mobile-realtime-feed"),
    path("copilot/", MobileCopilotView.as_view(), name="mobile-copilot"),
    path("field/seizure/", RegulatorSeizureWorkflowView.as_view(), name="mobile-seizure-workflow"),
    path("field/customs-hold/", CustomsShipmentHoldView.as_view(), name="mobile-customs-hold"),
    path("field/warehouse-transfer/", WarehouseTransferConfirmView.as_view(), name="mobile-warehouse-transfer"),
    path("field/pharmacy-recall-ack/", PharmacyRecallAckWorkflowView.as_view(), name="mobile-pharmacy-recall-ack"),
]
