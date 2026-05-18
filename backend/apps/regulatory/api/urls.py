from django.urls import path

from apps.regulatory.api.views import (
    BatchApproveView,
    BatchAuditTrailView,
    BatchRecallAffectedView,
    BatchRecallView,
    BatchRejectView,
    BatchSuspendView,
    PendingBatchesView,
    RegulatorSerialLookupView,
    RegulatorSovereignVerifyView,
)

urlpatterns = [
    path("batches/recall-affected/", BatchRecallAffectedView.as_view(), name="regulatory-batch-recall-affected"),
    path("batches/pending/", PendingBatchesView.as_view(), name="regulatory-pending-batches"),
    path("batches/<uuid:pk>/approve/", BatchApproveView.as_view(), name="regulatory-batch-approve"),
    path("batches/<uuid:pk>/reject/", BatchRejectView.as_view(), name="regulatory-batch-reject"),
    path("batches/<uuid:pk>/suspend/", BatchSuspendView.as_view(), name="regulatory-batch-suspend"),
    path("batches/<uuid:pk>/recall/", BatchRecallView.as_view(), name="regulatory-batch-recall"),
    path("batches/<uuid:pk>/audit-trail/", BatchAuditTrailView.as_view(), name="regulatory-batch-audit-trail"),
    path("verification/lookup/", RegulatorSerialLookupView.as_view(), name="regulatory-serial-lookup"),
    path("verification/authenticate/", RegulatorSovereignVerifyView.as_view(), name="regulatory-verify-authenticate"),
]
