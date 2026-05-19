"""Phase 20A.2 — national demo seed, context bundles, workflows."""
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient, APITestCase

from apps.accounts.models import Role
from apps.core.constants import RoleCode
from apps.explorer.services.context_aggregates import (
    CONTEXT_TO_AGGREGATE,
    aggregate_id_for_context,
    build_context_aggregate_bundle,
)
from apps.operational_demo.seed import is_seeded, seed_operational_demo_data

User = get_user_model()


class Phase20A2NationalDemoTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.reg_role, _ = Role.objects.get_or_create(code=RoleCode.NAFDAC_ADMIN, defaults={"name": "NAFDAC"})
        self.regulator = User.objects.create_user(
            username="reg_p20a2", password="pass", role=self.reg_role, is_regulator=True
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.regulator)

    def test_seed_lite_creates_dataset(self):
        if is_seeded():
            seed_operational_demo_data(lite=True, force=True)
        else:
            seed_operational_demo_data(lite=True)
        self.assertTrue(is_seeded())

    def test_executive_contexts_unique_aggregates(self):
        keys = [
            "medicine_stability",
            "counterfeit_risk_forecast",
            "api_health",
            "national_ai_intelligence",
        ]
        aggs = {aggregate_id_for_context(k) for k in keys}
        self.assertEqual(len(aggs), len(keys))

    def test_context_bundles_differ(self):
        seed_operational_demo_data(lite=True, force=True)
        b1 = build_context_aggregate_bundle(aggregate_id="medicine-stability-current")
        b2 = build_context_aggregate_bundle(aggregate_id="api-health-current")
        self.assertNotEqual(b1["summary"]["title"], b2["summary"]["title"])

    def test_context_bundle_api_paginates(self):
        seed_operational_demo_data(lite=True, force=True)
        r = self.client.get("/api/v1/explorer/context-bundle/", {"context": "open_alerts", "page": 1})
        self.assertEqual(r.status_code, 200)
        records = r.json()["data"]["records"]
        self.assertIn("items", records)

    def test_staff_endpoint(self):
        seed_operational_demo_data(lite=True, force=True)
        r = self.client.get("/api/v1/explorer/staff/")
        self.assertEqual(r.status_code, 200)
        self.assertGreaterEqual(len(r.json()["data"]["staff"]), 1)

    @patch("apps.copilot.services.briefing.generate_operational_briefing")
    def test_generate_briefing_action(self, mock_brief):
        mock_brief.return_value = {"summary": "Test", "disclaimer": "review", "available": True}
        seed_operational_demo_data(lite=True, force=True)
        r = self.client.post(
            "/api/v1/explorer/actions/national_risk/open-alerts-current/execute/",
            {"action_id": "generate_briefing"},
            format="json",
        )
        self.assertEqual(r.status_code, 201)
        self.assertTrue(r.json()["data"]["ok"])

    def test_context_map_complete(self):
        self.assertIn("counterfeit_detections", CONTEXT_TO_AGGREGATE)
