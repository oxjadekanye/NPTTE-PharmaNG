"""Phase 20B — sovereign AI copilot APIs."""
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase

from apps.accounts.models import Role
from apps.core.constants import RoleCode
from apps.copilot.constants import DISCLAIMER, HUMAN_REVIEW_REQUIRED
from apps.enforcement.models import EnforcementCase

User = get_user_model()


class Phase20BCopilotTests(APITestCase):
    def setUp(self):
        self.reg_role, _ = Role.objects.get_or_create(code=RoleCode.NAFDAC_ADMIN, defaults={"name": "NAFDAC"})
        self.regulator = User.objects.create_user(
            username="reg_p20b", password="pass", role=self.reg_role, is_regulator=True
        )
        self.case = EnforcementCase.objects.create(
            case_reference="ENF-P20B",
            title="Copilot case",
            summary="Test",
            case_status=EnforcementCase.STATUS_OPEN,
            severity=EnforcementCase.SEV_HIGH,
        )

    def test_explain_risk_national_context(self):
        c = APIClient()
        c.force_authenticate(user=self.regulator)
        r = c.post(
            "/api/v1/copilot/explain-risk/",
            {"context_key": "national_status", "prompt_mode": "explain_risk"},
            format="json",
        )
        self.assertEqual(r.status_code, 200)
        data = r.json()["data"]
        self.assertTrue(data["human_review_required"])
        self.assertEqual(data["disclaimer"], DISCLAIMER)
        self.assertIn("summary", data)
        self.assertIn("recommended_actions", data)

    def test_generate_briefing_enforcement_case(self):
        c = APIClient()
        c.force_authenticate(user=self.regulator)
        r = c.post(
            "/api/v1/copilot/generate-briefing/",
            {
                "entity_type": "enforcement_case",
                "entity_id": str(self.case.id),
                "prompt_mode": "generate_briefing",
            },
            format="json",
        )
        self.assertEqual(r.status_code, 200)
        self.assertIn("reasoning", r.json()["data"])

    def test_recommend_actions_requires_regulator(self):
        c = APIClient()
        r = c.post(
            "/api/v1/copilot/recommend-actions/",
            {"context_key": "national_status"},
            format="json",
        )
        self.assertEqual(r.status_code, 401)

    def test_executive_briefing(self):
        c = APIClient()
        c.force_authenticate(user=self.regulator)
        r = c.post("/api/v1/copilot/executive-briefing/", {}, format="json")
        self.assertEqual(r.status_code, 200)
        data = r.json()["data"]
        self.assertEqual(data["human_review_required"], HUMAN_REVIEW_REQUIRED)

    def test_draft_enforcement_note(self):
        c = APIClient()
        c.force_authenticate(user=self.regulator)
        r = c.post(
            "/api/v1/copilot/draft-enforcement-note/",
            {
                "entity_type": "enforcement_case",
                "entity_id": str(self.case.id),
            },
            format="json",
        )
        self.assertEqual(r.status_code, 200)
        self.assertIn("draft", r.json()["data"]["summary"].lower())

    def test_summarise_investigation(self):
        c = APIClient()
        c.force_authenticate(user=self.regulator)
        r = c.post(
            "/api/v1/copilot/summarise-investigation/",
            {
                "entity_type": "enforcement_case",
                "entity_id": str(self.case.id),
            },
            format="json",
        )
        self.assertEqual(r.status_code, 200)
