"""Phase 20A.6 — shell-first lite payloads."""
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase

from apps.accounts.models import Role
from apps.core.constants import RoleCode
from apps.explorer.services.quick_explorer import apply_lite_summary

User = get_user_model()


class LiteSummaryTests(APITestCase):
    def setUp(self):
        self.reg_role, _ = Role.objects.get_or_create(code=RoleCode.NAFDAC_ADMIN, defaults={"name": "NAFDAC"})
        self.regulator = User.objects.create_user(
            username="lite_reg_p20a6", password="pass", role=self.reg_role, is_regulator=True
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.regulator)

    def test_apply_lite_summary_strips_heavy_fields(self):
        full = {
            "context_key": "open_alerts",
            "title": "Open alerts",
            "count": 3,
            "recommended_actions": ["assign"],
            "top_organisations": ["Org A"],
        }
        lite = apply_lite_summary(full)
        self.assertIn("count", lite)
        self.assertNotIn("recommended_actions", lite)
        self.assertNotIn("top_organisations", lite)

    def test_quick_summary_lite_query_param(self):
        res = self.client.get("/api/v1/explorer/quick-summary/", {"context": "open_alerts", "lite": "1"})
        self.assertEqual(res.status_code, 200)
        data = res.json().get("data") or {}
        self.assertIn("count", data)
        self.assertNotIn("recommended_actions", data)
