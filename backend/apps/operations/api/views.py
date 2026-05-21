"""Phase 15 — operational persistence APIs (tenant-safe)."""
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.permissions import IsRegulatorUser
from apps.core.roles import is_regulator_user
from apps.operations.models import (
    ActivityFeedEntry,
    OperationalDocument,
    OperationalTask,
    RegulatorOperationalHistory,
    WorkflowTimelineEntry,
)
from apps.operations.services.documents import save_operational_document
from apps.operations.services.task_engine import finish_task, serialize_task
from apps.operations.services.tasks import create_operational_task
from apps.tenancy.services.tenant import (
    filter_queryset_for_tenant,
    get_active_organisation_id,
    user_can_access_organisation,
)


def _serialize_workflow(row: WorkflowTimelineEntry) -> dict:
    return {
        "id": str(row.id),
        "workflow_type": row.workflow_type,
        "title": row.title,
        "summary": row.summary,
        "organisation_id": str(row.organisation_id) if row.organisation_id else None,
        "entity_type": row.entity_type,
        "entity_id": str(row.entity_id) if row.entity_id else None,
        "created_at": row.created_at.isoformat(),
    }


class WorkflowTimelineView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = WorkflowTimelineEntry.objects.all().order_by("-created_at")
        qs = filter_queryset_for_tenant(request, qs, org_field="organisation_id", allow_null=False)
        if not is_regulator_user(request.user) and not request.user.is_superuser:
            org_id = get_active_organisation_id(request)
            if org_id:
                qs = qs.filter(organisation_id=org_id)
        rows = [_serialize_workflow(r) for r in qs[:100]]
        return api_response(data={"timeline": rows, "count": len(rows)}, message="Workflow timeline")


class RegulatorHistoryView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        qs = RegulatorOperationalHistory.objects.all().order_by("-created_at")[:200]
        org_id = request.GET.get("organisation_id")
        if org_id:
            qs = qs.filter(organisation_id=org_id)
        rows = [
            {
                "id": str(r.id),
                "action_type": r.action_type,
                "summary": r.summary,
                "organisation_id": str(r.organisation_id) if r.organisation_id else None,
                "actor": r.actor.username if r.actor else None,
                "created_at": r.created_at.isoformat(),
            }
            for r in qs
        ]
        return api_response(data={"history": rows, "count": len(rows)}, message="Regulator operational history")


class ActivityFeedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = ActivityFeedEntry.objects.all().order_by("-created_at")
        if is_regulator_user(request.user) or request.user.is_superuser:
            visibility = request.GET.get("visibility")
            if visibility:
                qs = qs.filter(visibility=visibility)
        else:
            org_id = get_active_organisation_id(request)
            qs = qs.filter(organisation_id=org_id) if org_id else qs.none()
        rows = [
            {
                "id": str(r.id),
                "feed_type": r.feed_type,
                "title": r.title,
                "summary": r.summary,
                "severity": r.severity,
                "organisation_id": str(r.organisation_id) if r.organisation_id else None,
                "created_at": r.created_at.isoformat(),
            }
            for r in qs[:100]
        ]
        return api_response(data={"feed": rows, "count": len(rows)}, message="Activity feed")


class OperationalTaskListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = OperationalTask.objects.all().order_by("due_at", "-created_at")
        qs = filter_queryset_for_tenant(request, qs, org_field="organisation_id", allow_null=True)
        status = request.GET.get("status")
        if status:
            qs = qs.filter(task_status=status)
        rows = [
            {
                "id": str(t.id),
                "title": t.title,
                "task_type": t.task_type,
                "task_status": t.task_status,
                "priority": t.priority,
                "due_at": t.due_at.isoformat() if t.due_at else None,
                "escalation_status": t.escalation_status,
                "organisation_id": str(t.organisation_id) if t.organisation_id else None,
            }
            for t in qs[:50]
        ]
        return api_response(data={"tasks": rows, "count": len(rows)}, message="Operational tasks")

    def post(self, request):
        org_id = request.data.get("organisation_id") or get_active_organisation_id(request)
        from apps.organisations.models import Organisation

        organisation = Organisation.objects.filter(pk=org_id).first() if org_id else None
        if organisation and not user_can_access_organisation(request.user, organisation.id):
            return api_response(message="Organisation access denied", status_code=403)
        task = create_operational_task(
            title=request.data.get("title", "Operational task"),
            task_type=request.data.get("task_type", "review"),
            organisation=organisation,
            description=request.data.get("description", ""),
            priority=request.data.get("priority", "normal"),
            created_by=request.user,
        )
        return api_response(
            data={"id": str(task.id), "title": task.title},
            message="Task created",
            status_code=201,
        )


class OperationalTaskCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        task = OperationalTask.objects.get(pk=pk)
        if task.organisation_id and not user_can_access_organisation(request.user, task.organisation_id):
            return api_response(message="Access denied", status_code=403)
        finish_task(task=task, actor=request.user)
        return api_response(data=serialize_task(task), message="Task completed")


class DocumentUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = OperationalDocument.objects.all().order_by("-created_at")
        qs = filter_queryset_for_tenant(request, qs, org_field="organisation_id", allow_null=False)
        rows = [
            {
                "id": str(d.id),
                "title": d.title,
                "document_type": d.document_type,
                "original_filename": d.original_filename,
                "file_size": d.file_size,
                "organisation_id": str(d.organisation_id),
                "created_at": d.created_at.isoformat(),
            }
            for d in qs[:50]
        ]
        return api_response(data={"documents": rows, "count": len(rows)}, message="Documents")

    def post(self, request):
        org_id = request.data.get("organisation_id") or get_active_organisation_id(request)
        from apps.organisations.models import Organisation

        organisation = Organisation.objects.get(pk=org_id)
        if not user_can_access_organisation(request.user, organisation.id):
            return api_response(message="Organisation access denied", status_code=403)
        uploaded = request.FILES.get("file")
        if not uploaded:
            return api_response(message="file required", status_code=400)
        doc = save_operational_document(
            organisation=organisation,
            document_type=request.data.get("document_type", OperationalDocument.DOC_COMPLIANCE),
            title=request.data.get("title", uploaded.name),
            uploaded_file=uploaded,
            uploaded_by=request.user,
        )
        return api_response(
            data={"id": str(doc.id), "storage_key": doc.storage_key},
            message="Document uploaded",
            status_code=201,
        )


class OrganisationSettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        org_id = request.GET.get("organisation_id") or get_active_organisation_id(request)
        from apps.organisations.models import Organisation
        from apps.onboarding.models import OrganisationOnboarding

        if not org_id:
            return api_response(message="organisation_id required", status_code=400)
        if not user_can_access_organisation(request.user, org_id):
            return api_response(message="Access denied", status_code=403)
        org = Organisation.objects.get(pk=org_id)
        onboarding = OrganisationOnboarding.objects.filter(organisation=org).order_by("-created_at").first()
        doc_count = OperationalDocument.objects.filter(organisation=org).count()
        open_tasks = OperationalTask.objects.filter(
            organisation=org, task_status=OperationalTask.STATUS_OPEN
        ).count()
        return api_response(
            data={
                "organisation_id": str(org.id),
                "legal_name": org.legal_name,
                "trading_name": org.trading_name,
                "email": org.email,
                "phone_number": org.phone_number,
                "city": org.city,
                "state": org.state,
                "license_number": org.license_number,
                "onboarding_status": onboarding.status if onboarding else None,
                "document_count": doc_count,
                "open_tasks": open_tasks,
                "operational_readiness": "ready" if org.is_active and doc_count > 0 else "pending",
                "branding_logo_url": org.metadata.get("logo_url", ""),
            },
            message="Organisation settings",
        )

    def patch(self, request):
        org_id = request.data.get("organisation_id") or get_active_organisation_id(request)
        from apps.organisations.models import Organisation

        org = Organisation.objects.get(pk=org_id)
        if not user_can_access_organisation(request.user, org.id):
            return api_response(message="Access denied", status_code=403)
        for field in ("email", "phone_number", "trading_name", "city", "state"):
            if field in request.data:
                setattr(org, field, request.data[field])
        if "logo_url" in request.data:
            org.metadata = {**org.metadata, "logo_url": request.data["logo_url"]}
        org.save()
        return api_response(data={"organisation_id": str(org.id)}, message="Settings updated")


class OrganisationProfileView(OrganisationSettingsView):
    """Alias for organisation profile management."""
