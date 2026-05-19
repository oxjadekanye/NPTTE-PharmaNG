from django.urls import path

from apps.command_orchestration.api.views import (
    CommandRoomSnapshotView,
    InvestigationRoomView,
    MapMarkersView,
    RegionalDetailView,
    RegionalListView,
    TaskOrchestrationView,
)

urlpatterns = [
    path("map-markers/", MapMarkersView.as_view(), name="orchestration-map-markers"),
    path("regions/", RegionalListView.as_view(), name="orchestration-regions"),
    path("regions/<str:region_key>/", RegionalDetailView.as_view(), name="orchestration-region-detail"),
    path("command-room/", CommandRoomSnapshotView.as_view(), name="orchestration-command-room"),
    path("tasks/live/", TaskOrchestrationView.as_view(), name="orchestration-tasks-live"),
    path("investigations/<uuid:case_id>/room/", InvestigationRoomView.as_view(), name="investigation-room"),
]
