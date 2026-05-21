"""Phase 11 — national operational hardening APIs."""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from apps.accounts.models import Role
from apps.core.constants import RoleCode
from apps.operations.models import OperationalTask
from apps.operations.services.tasks import create_operational_task

User = get_user_model()


class Phase11NationalOperationalTests(APITestCase):
    def setUp(self):
        role, _ = Role.objects.get_or_create(code=RoleCode.NAFDAC_ADMIN, defaults={"name": "NAFDAC"})
        self.user = User.objects.create_user(
            username="p11_ops_regulator",
            email="p11ops@test.ng",
            password="TestPass2026!",
            role=role,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_operational_feed_polling(self):
        r = self.client.get("/api/v1/realtime/operational-feed/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        data = r.json()["data"]
        self.assertIn("events", data)
        self.assertIn("polled_at", data)
        self.assertEqual(data.get("transport"), "polling")

    def test_prefetch_manifest(self):
        r = self.client.get("/api/v1/realtime/prefetch/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn("feed_url", r.json()["data"])

    def test_national_operations_metrics(self):
        r = self.client.get("/api/v1/intelligence/national-operations/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        data = r.json()["data"]
        self.assertIn("national_operational_readiness_score", data)
        self.assertIn("disclaimer", data)

    def test_task_escalation_and_overdue(self):
        task = create_operational_task(
            title="Phase 11 test task",
            task_type="field_inspection",
            created_by=self.user,
            due_in_days=1,
        )
        task.due_at = timezone.now() - timedelta(hours=1)
        task.save(update_fields=["due_at"])
        esc = self.client.post(f"/api/v1/operations/tasks/{task.id}/escalate/", {"reason": "test"}, format="json")
        self.assertEqual(esc.status_code, status.HTTP_200_OK)
        self.assertEqual(esc.json()["data"]["escalation_status"], "escalated")
        od = self.client.get("/api/v1/operations/tasks/overdue/")
        self.assertEqual(od.status_code, status.HTTP_200_OK)

    def test_alert_center(self):
        r = self.client.get("/api/v1/alerts/center/")
        if r.status_code == 200 and r.json()["data"]["alerts"]:
            first = r.json()["data"]["alerts"][0]
            self.assertIn("organisation_name", first)
            self.assertIn("address_line", first)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn("alerts", r.json()["data"])

    def test_citizen_verification_history_public(self):
        r = self.client.get("/api/v1/public/verification-history/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn("history", r.json()["data"])

    def test_mobile_evidence_timeline(self):
        r = self.client.get("/api/v1/mobile/evidence/timeline/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
