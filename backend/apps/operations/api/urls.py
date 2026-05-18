from django.urls import path

from apps.operations.api.views import (
    ActivityFeedView,
    DocumentUploadView,
    OperationalTaskCompleteView,
    OperationalTaskListView,
    OrganisationProfileView,
    OrganisationSettingsView,
    RegulatorHistoryView,
    WorkflowTimelineView,
)

urlpatterns = [
    path("workflow/timeline/", WorkflowTimelineView.as_view(), name="ops-workflow-timeline"),
    path("regulator/history/", RegulatorHistoryView.as_view(), name="ops-regulator-history"),
    path("activity/feed/", ActivityFeedView.as_view(), name="ops-activity-feed"),
    path("tasks/", OperationalTaskListView.as_view(), name="ops-tasks"),
    path("tasks/<uuid:pk>/complete/", OperationalTaskCompleteView.as_view(), name="ops-task-complete"),
    path("documents/", DocumentUploadView.as_view(), name="ops-documents"),
    path("organisation/settings/", OrganisationSettingsView.as_view(), name="ops-org-settings"),
    path("organisation/profile/", OrganisationProfileView.as_view(), name="ops-org-profile"),
]
