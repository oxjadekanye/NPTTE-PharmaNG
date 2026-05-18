"""Phase 16 — integration APIs (tenant-safe where applicable)."""
from django.http import FileResponse
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.permissions import IsRegulatorUser
from apps.core.roles import is_regulator_user
from apps.developer_access.models import ApiDeveloperKey
from apps.developer_access.services import create_api_key, log_api_request, revoke_api_key, rotate_api_key
from apps.integrations.analytics.snapshots import persist_operational_analytics
from apps.integrations.exports.engine import create_export_job, run_export_job
from apps.integrations.models import (
    AnalyticsSnapshot,
    EmailDeliveryLog,
    ExportJob,
    ExternalIntegrationConnector,
    ProviderHealthStatus,
    SMSDeliveryLog,
    WebhookDeliveryLog,
    WebhookSubscription,
)
from apps.integrations.pdf.generator import (
    generate_batch_certificate_pdf,
    generate_qr_label_pdf,
    generate_recall_notice_pdf,
)
from apps.integrations.providers.email import resolve_email_provider
from apps.integrations.providers.push import push_health, register_push_device, send_push_to_user
from apps.integrations.providers.sms import resolve_sms_provider, send_sms_with_logging
from apps.integrations.storage.backends import get_storage_backend, save_integration_file
from apps.integrations.webhooks.dispatcher import dispatch_webhook_event, publish_integration_event
from apps.tenancy.services.tenant import filter_queryset_for_tenant, get_active_organisation_id, user_can_access_organisation


class IntegrationHealthView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        email = resolve_email_provider().health_check()
        sms = resolve_sms_provider().health_check()
        storage = get_storage_backend().health_check()
        push = push_health()
        webhook_count = WebhookDeliveryLog.objects.filter(delivery_status="failed").count()
        providers = [
            {"type": "email", "name": resolve_email_provider().name, "status": email[0], "message": email[1]},
            {"type": "sms", "name": resolve_sms_provider().name, "status": sms[0], "message": sms[1]},
            {"type": "storage", "name": get_storage_backend().name, "status": storage[0], "message": storage[1]},
            {"type": "push", "name": "web_push_mock", "status": push[0], "message": push[1]},
            {
                "type": "webhook",
                "name": "outbound",
                "status": ProviderHealthStatus.STATUS_DEGRADED if webhook_count else ProviderHealthStatus.STATUS_HEALTHY,
                "message": f"{webhook_count} failed deliveries (24h window)",
            },
        ]
        persisted = list(ProviderHealthStatus.objects.values("provider_type", "provider_name", "status", "message"))
        pending_exports = ExportJob.objects.filter(job_status=ExportJob.STATUS_PENDING).count()
        return api_response(
            data={
                "providers": providers,
                "persisted_health": persisted,
                "notification_queue": {"pending_exports": pending_exports},
                "checked_at": timezone.now().isoformat(),
            },
            message="Integration health dashboard",
        )


class WebhookSubscriptionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = WebhookSubscription.objects.filter(is_active_subscription=True).order_by("-created_at")
        qs = filter_queryset_for_tenant(request, qs, org_field="organisation_id", allow_null=True)
        rows = [
            {
                "id": str(s.id),
                "target_url": s.target_url,
                "subscribed_events": s.subscribed_events,
                "organisation_id": str(s.organisation_id) if s.organisation_id else None,
            }
            for s in qs[:50]
        ]
        return api_response(data={"subscriptions": rows}, message="Webhook subscriptions")

    def post(self, request):
        from apps.organisations.models import Organisation

        org_id = request.data.get("organisation_id") or get_active_organisation_id(request)
        organisation = Organisation.objects.filter(pk=org_id).first() if org_id else None
        if organisation and not user_can_access_organisation(request.user, organisation.id):
            return api_response(message="Access denied", status_code=403)
        sub = WebhookSubscription.objects.create(
            organisation=organisation,
            target_url=request.data["target_url"],
            secret=request.data.get("secret", ""),
            subscribed_events=request.data.get("subscribed_events", [WebhookSubscription.EVENT_RECALL_CREATED]),
            created_by=request.user,
        )
        return api_response(data={"id": str(sub.id)}, message="Webhook subscription created", status_code=201)


class WebhookDeliveryLogView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        logs = WebhookDeliveryLog.objects.select_related("subscription").order_by("-created_at")[:100]
        rows = [
            {
                "id": str(l.id),
                "event_type": l.event_type,
                "delivery_status": l.delivery_status,
                "http_status": l.http_status,
                "retry_count": l.retry_count,
                "created_at": l.created_at.isoformat(),
            }
            for l in logs
        ]
        return api_response(data={"deliveries": rows}, message="Webhook delivery logs")


class WebhookTestView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def post(self, request):
        event_type = request.data.get("event_type", WebhookSubscription.EVENT_RECALL_CREATED)
        payload = request.data.get("payload", {"test": True})
        logs = publish_integration_event(event_type=event_type, payload=payload)
        return api_response(data={"dispatched": len(logs)}, message="Test event published", status_code=201)


class ExportJobListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = ExportJob.objects.all().order_by("-created_at")
        qs = filter_queryset_for_tenant(request, qs, org_field="organisation_id", allow_null=True)
        rows = [
            {
                "id": str(j.id),
                "report_type": j.report_type,
                "export_format": j.export_format,
                "job_status": j.job_status,
                "row_count": j.row_count,
                "storage_key": j.storage_key,
                "created_at": j.created_at.isoformat(),
            }
            for j in qs[:50]
        ]
        return api_response(data={"exports": rows}, message="Export jobs")

    def post(self, request):
        from apps.organisations.models import Organisation

        org_id = request.data.get("organisation_id") or get_active_organisation_id(request)
        organisation = Organisation.objects.filter(pk=org_id).first() if org_id else None
        if organisation and not user_can_access_organisation(request.user, organisation.id):
            return api_response(message="Access denied", status_code=403)
        job = create_export_job(
            report_type=request.data.get("report_type", ExportJob.REPORT_AUDIT),
            export_format=request.data.get("export_format", ExportJob.EXPORT_CSV),
            organisation=organisation,
            requested_by=request.user,
        )
        run_export_job(job=job)
        return api_response(
            data={"id": str(job.id), "status": job.job_status, "storage_key": job.storage_key},
            message="Export generated",
            status_code=201,
        )


class ExportDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        job = ExportJob.objects.get(pk=pk)
        if job.organisation_id and not user_can_access_organisation(request.user, job.organisation_id):
            return api_response(message="Access denied", status_code=403)
        if not job.storage_key:
            return api_response(message="Export not ready", status_code=404)
        from django.core.files.storage import default_storage

        if not default_storage.exists(job.storage_key):
            return api_response(message="File not found", status_code=404)
        f = default_storage.open(job.storage_key, "rb")
        content_type = "text/csv" if job.export_format == ExportJob.EXPORT_CSV else "application/pdf"
        return FileResponse(f, as_attachment=True, filename=f"nptte-{job.report_type}.{job.export_format}", content_type=content_type)


class PdfGenerateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        doc_type = request.data.get("document_type", "qr_label")
        if doc_type == "qr_label":
            content = generate_qr_label_pdf(
                serial_number=request.data.get("serial_number", "DEMO-SERIAL"),
                product_name=request.data.get("product_name", ""),
                batch_number=request.data.get("batch_number", ""),
            )
        elif doc_type == "batch_certificate":
            content = generate_batch_certificate_pdf(
                batch_number=request.data.get("batch_number", "BATCH-001"),
                product_name=request.data.get("product_name", "Product"),
                regulator_status=request.data.get("regulator_status", "approved"),
            )
        elif doc_type == "recall_notice":
            content = generate_recall_notice_pdf(
                recall_code=request.data.get("recall_code", "REC-001"),
                reason=request.data.get("reason", "Safety concern"),
            )
        else:
            return api_response(message="Unknown document_type", status_code=400)
        key = save_integration_file(folder="pdf", filename=f"{doc_type}.pdf", content=content, content_type="application/pdf")
        return api_response(data={"storage_key": key, "size_bytes": len(content)}, message="PDF generated", status_code=201)


class AnalyticsSnapshotView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = AnalyticsSnapshot.objects.order_by("-period_end")
        if not is_regulator_user(request.user) and not request.user.is_superuser:
            org_id = get_active_organisation_id(request)
            qs = qs.filter(organisation_id=org_id) if org_id else qs.none()
        rows = [
            {"id": str(s.id), "metric_type": s.metric_type, "metrics": s.metrics, "period_end": s.period_end.isoformat()}
            for s in qs[:20]
        ]
        return api_response(data={"snapshots": rows}, message="Analytics snapshots")

    def post(self, request):
        from apps.organisations.models import Organisation

        org_id = request.data.get("organisation_id") or get_active_organisation_id(request)
        organisation = Organisation.objects.filter(pk=org_id).first() if org_id else None
        snap = persist_operational_analytics(organisation=organisation)
        return api_response(data={"id": str(snap.id), "metrics": snap.metrics}, message="Analytics persisted", status_code=201)


class ExternalConnectorListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = ExternalIntegrationConnector.objects.all().order_by("connector_type")
        qs = filter_queryset_for_tenant(request, qs, org_field="organisation_id", allow_null=False)
        rows = [
            {
                "id": str(c.id),
                "connector_type": c.connector_type,
                "connector_name": c.connector_name,
                "connection_status": c.connection_status,
                "endpoint_url": c.endpoint_url,
            }
            for c in qs
        ]
        return api_response(data={"connectors": rows}, message="External connectors")

    def post(self, request):
        from apps.organisations.models import Organisation

        org_id = request.data.get("organisation_id") or get_active_organisation_id(request)
        organisation = Organisation.objects.get(pk=org_id)
        if not user_can_access_organisation(request.user, organisation.id):
            return api_response(message="Access denied", status_code=403)
        conn = ExternalIntegrationConnector.objects.create(
            organisation=organisation,
            connector_type=request.data.get("connector_type", ExternalIntegrationConnector.CONNECTOR_PHARMACY),
            connector_name=request.data.get("connector_name", "Integration"),
            endpoint_url=request.data.get("endpoint_url", ""),
            connection_status="configured",
            metadata=request.data.get("config", {}),
            created_by=request.user,
        )
        return api_response(data={"id": str(conn.id)}, message="Connector configured", status_code=201)


class PushRegisterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        reg = register_push_device(
            user=request.user,
            platform=request.data.get("platform", "web"),
            endpoint=request.data.get("endpoint", ""),
            keys=request.data.get("keys"),
        )
        return api_response(data={"id": str(reg.id)}, message="Push device registered", status_code=201)


class PushTestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        count = send_push_to_user(
            user=request.user,
            title=request.data.get("title", "NPTTE Alert"),
            body=request.data.get("body", "Test push notification"),
        )
        return api_response(data={"devices_notified": count}, message="Push dispatched")


class SmsSendView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def post(self, request):
        log = send_sms_with_logging(
            phone_number=request.data["phone_number"],
            message=request.data.get("message", "NPTTE alert"),
            notification_type=request.data.get("notification_type", "regulator_escalation"),
        )
        return api_response(data={"id": str(log.id), "status": log.delivery_status}, message="SMS dispatched", status_code=201)


class DeliveryLogsView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        email_logs = list(
            EmailDeliveryLog.objects.order_by("-created_at")[:25].values(
                "recipient", "subject", "provider_name", "delivery_status", "created_at"
            )
        )
        sms_logs = list(
            SMSDeliveryLog.objects.order_by("-created_at")[:25].values(
                "phone_number", "provider_name", "delivery_status", "created_at"
            )
        )
        return api_response(data={"email": email_logs, "sms": sms_logs}, message="Delivery logs")


class IntegrationApiKeysView(APIView):
    """Extended API key management — regulator and org admins."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = ApiDeveloperKey.objects.order_by("-created_at")
        if not is_regulator_user(request.user) and not request.user.is_superuser:
            org_id = get_active_organisation_id(request)
            qs = qs.filter(organisation_id=org_id) if org_id else qs.none()
        rows = [
            {
                "id": str(k.id),
                "name": k.name,
                "prefix": k.key_prefix,
                "scopes": k.scopes,
                "active": k.is_active_key,
                "last_used_at": k.last_used_at.isoformat() if k.last_used_at else None,
            }
            for k in qs[:50]
        ]
        return api_response(data={"keys": rows}, message="API keys")

    def post(self, request):
        from apps.organisations.models import Organisation

        org_id = request.data.get("organisation_id") or get_active_organisation_id(request)
        organisation = Organisation.objects.filter(pk=org_id).first() if org_id else None
        if organisation and not user_can_access_organisation(request.user, organisation.id):
            return api_response(message="Access denied", status_code=403)
        if not is_regulator_user(request.user) and not organisation:
            return api_response(message="organisation_id required", status_code=400)
        key, raw = create_api_key(
            name=request.data["name"],
            organisation=organisation,
            scopes=request.data.get("scopes", ["verify.read"]),
            actor=request.user,
        )
        log_api_request(api_key=key, path="/integrations/keys/", method="POST", status_code=201)
        return api_response(
            data={"id": str(key.id), "key_prefix": key.key_prefix, "api_key_once": raw, "scopes": key.scopes},
            message="API key created",
            status_code=201,
        )


class IntegrationApiKeyRevokeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        key = ApiDeveloperKey.objects.get(pk=pk)
        if key.organisation_id and not user_can_access_organisation(request.user, key.organisation_id):
            if not is_regulator_user(request.user):
                return api_response(message="Access denied", status_code=403)
        revoke_api_key(key=key, actor=request.user)
        return api_response(data={"id": str(key.id)}, message="API key revoked")


class IntegrationApiKeyRotateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        key = ApiDeveloperKey.objects.get(pk=pk)
        if key.organisation_id and not user_can_access_organisation(request.user, key.organisation_id):
            if not is_regulator_user(request.user):
                return api_response(message="Access denied", status_code=403)
        new_key, raw = rotate_api_key(key=key, actor=request.user)
        return api_response(
            data={"id": str(new_key.id), "api_key_once": raw, "key_prefix": new_key.key_prefix},
            message="API key rotated",
        )
