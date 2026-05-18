"""Phase 9 — national ecosystem additive API (events national summary)."""
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from apps.accounts.models import Role
from apps.core.constants import RoleCode

User = get_user_model()


class NationalOperationsSummaryTests(APITestCase):
    def setUp(self):
        role, _ = Role.objects.get_or_create(code=RoleCode.NAFDAC_ADMIN, defaults={"name": "NAFDAC"})
        self.regulator = User.objects.create_user(
            username="p9_regulator",
            email="p9@test.ng",
            password="TestPass2026!",
            role=role,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.regulator)

    def test_national_summary_ok(self):
        response = self.client.get("/api/v1/events/national-summary/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        self.assertTrue(body.get("success"))
        data = body.get("data") or {}
        self.assertIn("national_threat_index", data)
        self.assertIn("recent_event_sample", data)
        self.assertIsInstance(data["recent_event_sample"], list)

    def test_national_summary_requires_auth(self):
        anon = APIClient()
        response = anon.get("/api/v1/events/national-summary/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
