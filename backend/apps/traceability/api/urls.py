from django.urls import path

from apps.traceability.api.custody_views import (
    CustodyRecordView,
    CustodyTimelineView,
    RecallExecutionLaunchView,
    RecallExecutionListView,
    RecallPharmacyAcknowledgeView,
    RecallWarehouseAcknowledgeView,
)
from apps.traceability.api.phase12_views import (
    RecallOrchestrationCenterView,
    SupplyChainCustodyExplorerView,
    SupplyChainShipmentTimelineView,
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
    path(
        "recall-execution/pharmacy-ack/",
        RecallPharmacyAcknowledgeView.as_view(),
        name="recall-pharmacy-ack",
    ),
    path(
        "recall-execution/warehouse-ack/",
        RecallWarehouseAcknowledgeView.as_view(),
        name="recall-warehouse-ack",
    ),
    path("supply-chain/shipments/", SupplyChainShipmentTimelineView.as_view(), name="supply-chain-shipments"),
    path("supply-chain/custody/", SupplyChainCustodyExplorerView.as_view(), name="supply-chain-custody"),
    path("recall-orchestration/", RecallOrchestrationCenterView.as_view(), name="recall-orchestration"),
]
