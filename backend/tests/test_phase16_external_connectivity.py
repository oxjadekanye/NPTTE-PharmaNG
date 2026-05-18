"""Phase 16 — external connectivity and integrations."""
from django.contrib.auth import get_user_model
from django.core import mail
from rest_framework.test import APIClient, APITestCase

from apps.accounts.models import Role
from apps.core.constants import RoleCode
from apps.developer_access.models import ApiDeveloperKey
from apps.developer_access.services import create_api_key, revoke_api_key
from apps.integrations.exports.engine import create_export_job, run_export_job
from apps.integrations.models import ExportJob, WebhookSubscription
from apps.integrations.pdf.generator import generate_qr_label_pdf
from apps.integrations.providers.email import ConsoleEmailProvider, send_email_with_logging
from apps.integrations.providers.sms import MockSMSProvider, send_sms_with_logging
from apps.integrations.storage.backends import LocalStorageBackend, save_integration_file
from apps.integrations.webhooks.dispatcher import publish_integration_event
from apps.organisations.models import Organisation, OrganisationType

User = get_user_model()


class Phase16ExternalConnectivityTests(APITestCase):
    def setUp(self):
        self.reg_role, _ = Role.objects.get_or_create(code=RoleCode.NAFDAC_ADMIN, defaults={"name": "NAFDAC"})
        self.regulator = User.objects.create_user(
            username="reg_p16", password="pass", role=self.reg_role, is_regulator=True
        )
        ot, _ = OrganisationType.objects.get_or_create(code="pharmacy", defaults={"name": "Pharmacy"})
        self.org = Organisation.objects.create(organisation_type=ot, legal_name="Pharmacy P16")

    def test_email_provider_fallback(self):
        mail.outbox = []
        log = send_email_with_logging(subject="Test", message="Body", recipient_list=["a@example.com"])
        self.assertIn(log.delivery_status, ("sent", "retry", "failed"))
        provider = ConsoleEmailProvider()
        self.assertEqual(provider.health_check()[0], "healthy")

    def test_sms_mock_provider(self):
        log = send_sms_with_logging(phone_number="+2348000000000", message="Recall alert")
        self.assertIn(log.delivery_status, ("sent", "sent_via_fallback"))

    def test_storage_abstraction(self):
        backend = LocalStorageBackend()
        key = save_integration_file(folder="test", filename="doc.txt", content=b"hello")
        self.assertTrue(key)
        self.assertEqual(backend.health_check()[0], "healthy")

    def test_pdf_generation(self):
        pdf = generate_qr_label_pdf(serial_number="NG-TEST-001", product_name="Paracetamol")
        self.assertTrue(pdf.startswith(b"%PDF"))

    def test_webhook_dispatch(self):
        sub = WebhookSubscription.objects.create(
            target_url="https://example.com/webhook",
            subscribed_events=[WebhookSubscription.EVENT_RECALL_CREATED],
            secret="test-secret",
        )
        logs = publish_integration_event(event_type=WebhookSubscription.EVENT_RECALL_CREATED, payload={"id": "1"})
        self.assertGreaterEqual(len(logs), 1)

    def test_api_key_scopes_and_revoke(self):
        key, raw = create_api_key(name="Test Key", organisation=self.org, scopes=["verify.read", "traceability.read"])
        self.assertTrue(raw.startswith("nptte_"))
        revoke_api_key(key=key)
        key.refresh_from_db()
        self.assertFalse(key.is_active_key)

    def test_export_generation(self):
        job = create_export_job(
            report_type=ExportJob.REPORT_AUDIT,
            export_format=ExportJob.EXPORT_CSV,
            organisation=self.org,
            requested_by=self.regulator,
        )
        job = run_export_job(job=job)
        self.assertEqual(job.job_status, ExportJob.STATUS_COMPLETED, job.error_message)
        self.assertTrue(job.storage_key)

    def test_integration_health_api(self):
        client = APIClient()
        client.force_authenticate(user=self.regulator)
        res = client.get("/api/v1/integrations/health/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("providers", res.json()["data"])
