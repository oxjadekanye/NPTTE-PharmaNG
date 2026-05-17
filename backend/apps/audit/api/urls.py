from django.urls import path

from apps.audit.api.views import AuditLogListView

urlpatterns = [
    path("logs/", AuditLogListView.as_view(), name="audit-logs"),
]
