from django.urls import path

from apps.explorer.api.views import (
    ExplorerActionsView,
    ExplorerDetailView,
    ExplorerEvidenceView,
    ExplorerExecuteActionView,
    ExplorerRelatedView,
    ExplorerResolveView,
    ExplorerRiskBreakdownView,
    ExplorerTimelineView,
)

urlpatterns = [
    path("resolve/", ExplorerResolveView.as_view(), name="explorer-resolve"),
    path("detail/<str:entity_type>/<str:entity_id>/", ExplorerDetailView.as_view(), name="explorer-detail"),
    path("related/<str:entity_type>/<str:entity_id>/", ExplorerRelatedView.as_view(), name="explorer-related"),
    path("timeline/<str:entity_type>/<str:entity_id>/", ExplorerTimelineView.as_view(), name="explorer-timeline"),
    path("evidence/<str:entity_type>/<str:entity_id>/", ExplorerEvidenceView.as_view(), name="explorer-evidence"),
    path(
        "actions/<str:entity_type>/<str:entity_id>/execute/",
        ExplorerExecuteActionView.as_view(),
        name="explorer-execute",
    ),
    path("actions/<str:entity_type>/<str:entity_id>/", ExplorerActionsView.as_view(), name="explorer-actions"),
    path(
        "risk-breakdown/<str:entity_type>/<str:entity_id>/",
        ExplorerRiskBreakdownView.as_view(),
        name="explorer-risk-breakdown",
    ),
]
