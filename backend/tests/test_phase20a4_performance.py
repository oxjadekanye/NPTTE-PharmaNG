"""Phase 20A.4 — ultra performance: lightweight APIs, cache, invalidation."""
from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.test import APIClient, APITestCase

from apps.accounts.models import Role
from apps.core.constants import RoleCode
from apps.explorer.services.cache import PREFIX, _cache_key, invalidate_context
from apps.explorer.services.context_summary import build_context_summary
from apps.explorer.services.invalidate import on_streambus_event
from apps.streambus.constants import EVT_SCAN

User = get_user_model()


class Phase20A4PerformanceTests(APITestCase):
    def setUp(self):
        self.reg_role, _ = Role.objects.get_or_create(code=RoleCode.NAFDAC_ADMIN, defaults={"name": "NAFDAC"})
        self.regulator = User.objects.create_user(
            username="reg_p20a4", password="pass", role=self.reg_role, is_regulator=True
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.regulator)

    def test_context_summary_shape(self):
        r = self.client.get("/api/v1/explorer/context-summary/", {"context": "open_alerts"})
        self.assertEqual(r.status_code, 200)
        data = r.json()["data"]
        self.assertIn("title", data)
        self.assertIn("count", data)
        self.assertIn("top_records", data)
        self.assertIn("severity_distribution", data)
        self.assertLessEqual(len(data.get("top_records") or []), 5)

    def test_context_records_pagination(self):
        r = self.client.get(
            "/api/v1/explorer/context-records/",
            {"context": "open_alerts", "page": 1, "page_size": 10},
        )
        self.assertEqual(r.status_code, 200)
        records = r.json()["data"]["records"]
        self.assertIn("items", records)
        self.assertLessEqual(len(records["items"]), 10)

    def test_cache_key_includes_entity_for_invalidation(self):
        key = _cache_key(
            scope="overview",
            entity_type="national_risk",
            entity_id="open-alerts-current",
            user_id="1",
        )
        self.assertIn("national_risk", key)
        self.assertIn("open-alerts-current", key)
        self.assertTrue(key.startswith(PREFIX))

    def test_targeted_streambus_invalidation(self):
        invalidate_context("open_alerts")
        on_streambus_event(event_type=EVT_SCAN, payload={"explorer_entity_type": "scan_event", "explorer_entity_id": "x"})
        summary = build_context_summary(context_key="open_alerts", request=None)
        self.assertIn("count", summary)

    @override_settings(OPENAI_API_KEY="")
    def test_briefing_deterministic_without_openai(self):
        from apps.copilot.services.briefing import generate_operational_briefing

        out = generate_operational_briefing(
            explorer_bundle={"summary": {"title": "Test"}, "records": [], "record_count": 0}
        )
        self.assertTrue(out.get("available"))
        self.assertEqual(out.get("source"), "deterministic")
