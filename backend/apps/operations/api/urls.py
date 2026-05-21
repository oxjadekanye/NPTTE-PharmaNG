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
from apps.operations.api.task_views import (
    FieldOperationsFeedView,
    OperationalCalendarView,
    OperationalOverdueTasksView,
    OperationalTaskAssignView,
    OperationalTaskCreatePhase11View,
    OperationalTaskDetailView,
    OperationalTaskEscalateView,
    OperationalTaskEvidenceView,
    OperationalTaskNotesView,
)

urlpatterns = [
    path("workflow/timeline/", WorkflowTimelineView.as_view(), name="ops-workflow-timeline"),
    path("regulator/history/", RegulatorHistoryView.as_view(), name="ops-regulator-history"),
    path("activity/feed/", ActivityFeedView.as_view(), name="ops-activity-feed"),
    path("field-operations/feed/", FieldOperationsFeedView.as_view(), name="ops-field-feed"),
    path("tasks/", OperationalTaskListView.as_view(), name="ops-tasks"),
    path("tasks/create/", OperationalTaskCreatePhase11View.as_view(), name="ops-task-create-p11"),
    path("tasks/overdue/", OperationalOverdueTasksView.as_view(), name="ops-tasks-overdue"),
    path("tasks/calendar/", OperationalCalendarView.as_view(), name="ops-tasks-calendar"),
    path("tasks/<uuid:pk>/", OperationalTaskDetailView.as_view(), name="ops-task-detail"),
    path("tasks/<uuid:pk>/assign/", OperationalTaskAssignView.as_view(), name="ops-task-assign"),
    path("tasks/<uuid:pk>/escalate/", OperationalTaskEscalateView.as_view(), name="ops-task-escalate"),
    path("tasks/<uuid:pk>/notes/", OperationalTaskNotesView.as_view(), name="ops-task-notes"),
    path("tasks/<uuid:pk>/evidence/", OperationalTaskEvidenceView.as_view(), name="ops-task-evidence"),
    path("tasks/<uuid:pk>/complete/", OperationalTaskCompleteView.as_view(), name="ops-task-complete"),
    path("documents/", DocumentUploadView.as_view(), name="ops-documents"),
    path("organisation/settings/", OrganisationSettingsView.as_view(), name="ops-org-settings"),
    path("organisation/profile/", OrganisationProfileView.as_view(), name="ops-org-profile"),
]
