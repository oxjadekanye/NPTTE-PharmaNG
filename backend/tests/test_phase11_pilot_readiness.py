"""Phase 11 — pilot readiness APIs."""
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from apps.accounts.models import Role
from apps.core.constants import RoleCode

User = get_user_model()


class PilotReadinessTests(APITestCase):
    def setUp(self):
        role, _ = Role.objects.get_or_create(code=RoleCode.NAFDAC_ADMIN, defaults={"name": "NAFDAC"})
        self.user = User.objects.create_user(
            username="p11_regulator",
            email="p11@test.ng",
            password="TestPass2026!",
            role=role,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_readiness_report(self):
        r = self.client.get("/api/v1/pilot/readiness/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        data = r.json()["data"]
        self.assertIn("operational_readiness_score", data)
        self.assertIn("demo_checklists", data)

    def test_api_readiness(self):
        r = self.client.get("/api/v1/pilot/api-readiness/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn("groups", r.json()["data"])

    def test_demo_control_inventory(self):
        r = self.client.get("/api/v1/pilot/demo-control/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_security_no_secrets(self):
        r = self.client.get("/api/v1/pilot/security/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        data = r.json()["data"]
        self.assertFalse(data.get("secrets_exposed"))
