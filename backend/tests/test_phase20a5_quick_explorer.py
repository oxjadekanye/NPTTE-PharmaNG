"""Phase 20A.5 — quick explorer endpoints and executive context uniqueness."""
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase

from apps.accounts.models import Role
from apps.core.constants import RoleCode
from apps.explorer.services.context_aggregates import aggregate_id_for_context
from apps.explorer.services.quick_explorer import build_quick_summary, slim_record

User = get_user_model()


class Phase20A5QuickExplorerTests(APITestCase):
    def setUp(self):
        self.reg_role, _ = Role.objects.get_or_create(code=RoleCode.NAFDAC_ADMIN, defaults={"name": "NAFDAC"})
        self.regulator = User.objects.create_user(
            username="reg_p20a5", password="pass", role=self.reg_role, is_regulator=True
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.regulator)

    def test_quick_summary_shape(self):
        r = self.client.get("/api/v1/explorer/quick-summary/", {"context": "open_alerts"})
        self.assertEqual(r.status_code, 200)
        data = r.json()["data"]
        for key in ("title", "summary", "count", "severity_distribution", "top_states", "updated_at"):
            self.assertIn(key, data)

    def test_quick_records_pagination(self):
        r = self.client.get(
            "/api/v1/explorer/quick-records/",
            {"context": "open_alerts", "page": 1, "page_size": 5},
        )
        self.assertEqual(r.status_code, 200)
        records = r.json()["data"]["records"]
        self.assertIn("items", records)
        self.assertLessEqual(len(records["items"]), 5)

    def test_executive_contexts_are_unique(self):
        keys = {
            "api_health": aggregate_id_for_context("api_health"),
            "medicine_stability": aggregate_id_for_context("medicine_stability"),
            "urgent_actions": aggregate_id_for_context("urgent_actions"),
        }
        self.assertEqual(len(set(keys.values())), len(keys))

    def test_slim_record_strips_metadata(self):
        row = slim_record(
            {
                "id": "1",
                "title": "Test",
                "severity": "high",
                "metadata": {"huge": "payload"},
                "organisation": "Acme",
            }
        )
        self.assertNotIn("metadata", row)
        self.assertEqual(row["title"], "Test")
