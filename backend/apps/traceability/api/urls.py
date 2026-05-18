from django.urls import path

from apps.traceability.api.custody_views import (
    CustodyRecordView,
    CustodyTimelineView,
    RecallExecutionLaunchView,
    RecallExecutionListView,
)
from apps.traceability.api.views import (
    BatchRecallListView,
    SupplyChainTransactionCreateView,
    SupplyChainTransactionDetailView,
    SupplyChainTransactionListView,
)

urlpatterns = [
    path("transactions/", SupplyChainTransactionListView.as_view(), name="trace-list"),
    path("transactions/record/", SupplyChainTransactionCreateView.as_view(), name="trace-record"),
    path(
        "transactions/<uuid:audit_reference>/",
        SupplyChainTransactionDetailView.as_view(),
        name="trace-detail",
    ),
    path("recalls/", BatchRecallListView.as_view(), name="batch-recalls"),
    path("custody/timeline/", CustodyTimelineView.as_view(), name="custody-timeline"),
    path("custody/record/", CustodyRecordView.as_view(), name="custody-record"),
    path("recall-execution/", RecallExecutionListView.as_view(), name="recall-execution-list"),
    path("recall-execution/launch/", RecallExecutionLaunchView.as_view(), name="recall-execution-launch"),
]
