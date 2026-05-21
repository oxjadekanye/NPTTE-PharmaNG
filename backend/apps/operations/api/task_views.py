"""Phase 11 — operational task field operations APIs."""
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.permissions import IsRegulatorUser
from apps.core.roles import is_regulator_user
from apps.operations.models import OperationalTask
from apps.operations.services.task_engine import (
    append_task_note,
    assign_task,
    attach_evidence_ref,
    calendar_tasks,
    escalate_task,
    finish_task,
    overdue_tasks,
    serialize_task,
)
from apps.operations.services.tasks import create_operational_task
from apps.tenancy.services.tenant import get_active_organisation_id, user_can_access_organisation

User = get_user_model()


def _task_access(request, task: OperationalTask) -> bool:
    if is_regulator_user(request.user) or request.user.is_superuser:
        return True
    if task.organisation_id:
        return user_can_access_organisation(request.user, task.organisation_id)
    return task.assigned_to_id == request.user.id


class OperationalTaskDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        task = OperationalTask.objects.get(pk=pk)
        if not _task_access(request, task):
            return api_response(message="Access denied", status_code=403)
        return api_response(data=serialize_task(task), message="Task detail")


class OperationalTaskAssignView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def post(self, request, pk):
        task = OperationalTask.objects.get(pk=pk)
        username = request.data.get("username") or request.data.get("assignee")
        assignee = User.objects.filter(username=username).first() if username else None
        if not assignee:
            return api_response(message="Assignee not found", status_code=400)
        assign_task(task=task, assignee=assignee, actor=request.user)
        return api_response(data=serialize_task(task), message="Task assigned")


class OperationalTaskEscalateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        task = OperationalTask.objects.get(pk=pk)
        if not _task_access(request, task):
            return api_response(message="Access denied", status_code=403)
        escalate_task(task=task, actor=request.user, reason=request.data.get("reason", ""))
        return api_response(data=serialize_task(task), message="Task escalated")


class OperationalTaskNotesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        task = OperationalTask.objects.get(pk=pk)
        if not _task_access(request, task):
            return api_response(message="Access denied", status_code=403)
        text = request.data.get("text", "").strip()
        if not text:
            return api_response(message="Note text required", status_code=400)
        append_task_note(task=task, text=text, actor=request.user)
        return api_response(data=serialize_task(task), message="Note added")


class OperationalTaskEvidenceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        task = OperationalTask.objects.get(pk=pk)
        if not _task_access(request, task):
            return api_response(message="Access denied", status_code=403)
        evidence_id = request.data.get("evidence_id", "")
        if not evidence_id:
            return api_response(message="evidence_id required", status_code=400)
        attach_evidence_ref(task=task, evidence_id=str(evidence_id), label=request.data.get("label", ""))
        return api_response(data=serialize_task(task), message="Evidence linked")


class OperationalOverdueTasksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        org_id = request.GET.get("organisation_id") or get_active_organisation_id(request)
        rows = [serialize_task(t) for t in overdue_tasks(organisation_id=org_id)]
        return api_response(data={"tasks": rows, "count": len(rows)}, message="Overdue tasks")


class OperationalCalendarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        org_id = request.GET.get("organisation_id") or get_active_organisation_id(request)
        days = int(request.GET.get("days", 30))
        entries = calendar_tasks(organisation_id=org_id, days=days)
        return api_response(data={"calendar": entries, "count": len(entries)}, message="Task calendar")


class FieldOperationsFeedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.operations.models import ActivityFeedEntry

        qs = ActivityFeedEntry.objects.filter(feed_type__in=["task", "task_escalation", "inspection"]).order_by(
            "-created_at"
        )[:50]
        org_id = get_active_organisation_id(request)
        if org_id and not is_regulator_user(request.user):
            qs = qs.filter(organisation_id=org_id)
        rows = [
            {
                "id": str(r.id),
                "feed_type": r.feed_type,
                "title": r.title,
                "summary": r.summary,
                "severity": r.severity,
                "created_at": r.created_at.isoformat(),
            }
            for r in qs
        ]
        return api_response(data={"feed": rows, "count": len(rows)}, message="Field operations feed")


class OperationalTaskCreatePhase11View(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def post(self, request):
        from apps.organisations.models import Organisation

        org_id = request.data.get("organisation_id") or get_active_organisation_id(request)
        organisation = Organisation.objects.filter(pk=org_id).first() if org_id else None
        assignee = None
        if request.data.get("assignee"):
            assignee = User.objects.filter(username=request.data["assignee"]).first()
        due_days = request.data.get("due_in_days")
        task = create_operational_task(
            title=request.data.get("title", "Field operational task"),
            task_type=request.data.get("task_type", "field_inspection"),
            organisation=organisation,
            assigned_to=assignee,
            description=request.data.get("description", ""),
            priority=request.data.get("priority", "normal"),
            due_in_days=int(due_days) if due_days is not None else 7,
            related_entity_type=request.data.get("related_entity_type", ""),
            related_entity_id=request.data.get("related_entity_id"),
            created_by=request.user,
        )
        if request.data.get("evidence_id"):
            attach_evidence_ref(task=task, evidence_id=str(request.data["evidence_id"]))
        return api_response(data=serialize_task(task), message="Task created", status_code=201)
