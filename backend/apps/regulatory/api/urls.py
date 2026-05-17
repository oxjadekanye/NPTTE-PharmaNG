from django.urls import path

from apps.regulatory.api.views import BatchApproveView, BatchSuspendView, PendingBatchesView

urlpatterns = [
    path("batches/pending/", PendingBatchesView.as_view(), name="regulatory-pending-batches"),
    path("batches/<uuid:pk>/approve/", BatchApproveView.as_view(), name="regulatory-batch-approve"),
    path("batches/<uuid:pk>/suspend/", BatchSuspendView.as_view(), name="regulatory-batch-suspend"),
]
