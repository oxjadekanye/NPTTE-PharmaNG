"""Phase 15 — operational persistence and notifications."""
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient, APITestCase

from apps.accounts.models import Role
from apps.core.constants import RoleCode
from apps.notifications.models import Notification
from apps.notifications.services.delivery import deliver_notification
from apps.operations.models import OperationalDocument, OperationalTask, WorkflowTimelineEntry
from apps.organisations.models import Organisation, OrganisationType
from apps.tenancy.models import OrganisationMembership
from apps.tenancy.services.invitations import invite_user
from apps.traceability.models import BatchRecall, RecallExecutionCampaign
from apps.traceability.recall_execution import acknowledge_pharmacy_recall, launch_recall_campaign

User = get_user_model()


class Phase15OperationalPersistenceTests(APITestCase):
    def setUp(self):
        self.reg_role, _ = Role.objects.get_or_create(code=RoleCode.NAFDAC_ADMIN, defaults={"name": "NAFDAC"})
        self.mfg_role, _ = Role.objects.get_or_create(
            code=RoleCode.MANUFACTURER_ADMIN, defaults={"name": "Mfg Admin"}
        )
        self.regulator = User.objects.create_user(
            username="reg_p15", password="pass", role=self.reg_role, is_regulator=True
        )
        ot, _ = OrganisationType.objects.get_or_create(code="pharmacy", defaults={"name": "Pharmacy"})
        self.org_a = Organisation.objects.create(organisation_type=ot, legal_name="Pharmacy A")
        self.org_b = Organisation.objects.create(organisation_type=ot, legal_name="Pharmacy B")
        self.user_a = User.objects.create_user(
            username="user_p15a",
            password="pass",
            role=self.mfg_role,
            organisation=self.org_a,
            email="user_a@example.com",
        )
        self.user_b = User.objects.create_user(
            username="user_p15b", password="pass", role=self.mfg_role, organisation=self.org_b
        )
        OrganisationMembership.objects.create(
            user=self.user_a,
            organisation=self.org_a,
            role=self.mfg_role,
            membership_status=OrganisationMembership.STATUS_ACTIVE,
            is_primary=True,
        )

    def test_notification_creation(self):
        n = deliver_notification(
            recipient=self.user_a,
            title="Test alert",
            body="Body",
            organisation=self.org_a,
        )
        self.assertEqual(n.title, "Test alert")
        self.assertEqual(n.severity, "INFO")

    def test_invitation_email_generation(self):
        mail.outbox = []
        invite_user(
            organisation=self.org_a,
            email="invitee@example.com",
            role=self.mfg_role,
            invited_by=self.regulator,
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("invitation", mail.outbox[0].subject.lower())

    def test_tenant_safe_notifications(self):
        deliver_notification(
            recipient=self.user_a,
            title="Org A only",
            organisation=self.org_a,
        )
        deliver_notification(
            recipient=self.user_a,
            title="Org B only",
            organisation=self.org_b,
        )
        client = APIClient()
        client.force_authenticate(user=self.user_a)
        res = client.get(
            "/api/v1/notifications/center/",
            HTTP_X_NPTTE_ORGANISATION_CONTEXT=str(self.org_a.id),
        )
        self.assertEqual(res.status_code, 200)
        titles = [n["title"] for n in res.json()["data"]["notifications"]]
        self.assertIn("Org A only", titles)
        self.assertNotIn("Org B only", titles)

    def test_workflow_persistence(self):
        WorkflowTimelineEntry.objects.create(
            workflow_type="onboarding",
            title="Submitted",
            organisation=self.org_a,
        )
        client = APIClient()
        client.force_authenticate(user=self.user_a)
        res = client.get(
            "/api/v1/operations/workflow/timeline/",
            HTTP_X_NPTTE_ORGANISATION_CONTEXT=str(self.org_a.id),
        )
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(res.json()["data"]["count"], 1)

    def test_task_assignment(self):
        client = APIClient()
        client.force_authenticate(user=self.regulator)
        res = client.post(
            "/api/v1/operations/tasks/",
            {"title": "Review licence", "task_type": "onboarding_review", "organisation_id": str(self.org_a.id)},
            format="json",
        )
        self.assertEqual(res.status_code, 201)
        self.assertTrue(OperationalTask.objects.filter(organisation=self.org_a).exists())

    def test_document_ownership(self):
        client = APIClient()
        client.force_authenticate(user=self.user_a)
        f = SimpleUploadedFile("cac.pdf", b"pdf-content", content_type="application/pdf")
        res = client.post(
            "/api/v1/operations/documents/",
            {
                "organisation_id": str(self.org_a.id),
                "document_type": OperationalDocument.DOC_CAC,
                "title": "CAC Certificate",
                "file": f,
            },
            format="multipart",
        )
        self.assertEqual(res.status_code, 201)
        doc = OperationalDocument.objects.get(pk=res.json()["data"]["id"])
        self.assertEqual(doc.organisation_id, self.org_a.id)

    def test_recall_acknowledgement(self):
        from django.utils import timezone
        from apps.products.models import Product, ProductBatch

        product = Product.objects.create(
            name="Test Product",
            active_ingredient="Paracetamol",
            manufacturer=self.org_a,
        )
        batch = ProductBatch.objects.create(
            product=product,
            batch_number="BATCH-P15",
        )
        recall = BatchRecall.objects.create(
            batch=batch,
            recall_reason="Test recall",
            effective_at=timezone.now(),
        )
        campaign = launch_recall_campaign(batch_recall=recall, pharmacies_targeted=2, actor=self.regulator)
        ack = acknowledge_pharmacy_recall(
            campaign=campaign,
            pharmacy_organisation=self.org_a,
            completion_pct=100,
        )
        self.assertIsNotNone(ack.acknowledged_at)
        client = APIClient()
        client.force_authenticate(user=self.user_a)
        res = client.post(
            "/api/v1/traceability/recall-execution/pharmacy-ack/",
            {"campaign_id": str(campaign.id), "organisation_id": str(self.org_a.id)},
            format="json",
        )
        self.assertIn(res.status_code, (200, 201))

    def test_regulator_history(self):
        client = APIClient()
        client.force_authenticate(user=self.regulator)
        res = client.get("/api/v1/operations/regulator/history/")
        self.assertEqual(res.status_code, 200)
