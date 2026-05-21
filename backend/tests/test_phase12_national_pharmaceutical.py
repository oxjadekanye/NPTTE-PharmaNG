"""Phase 12 — national pharmaceutical intelligence & supply chain."""
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from apps.accounts.models import Role
from apps.core.constants import RoleCode

User = get_user_model()


class Phase12NationalPharmaceuticalTests(APITestCase):
    def setUp(self):
        role, _ = Role.objects.get_or_create(code=RoleCode.NAFDAC_ADMIN, defaults={"name": "NAFDAC"})
        self.user = User.objects.create_user(
            username="p12_regulator",
            email="p12@test.ng",
            password="TestPass2026!",
            role=role,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_medicine_intelligence_list(self):
        r = self.client.get("/api/v1/intelligence/medicines/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn("medicines", r.json()["data"])

    def test_shortage_and_counterfeit_risk(self):
        r1 = self.client.get("/api/v1/intelligence/shortage-risk/")
        r2 = self.client.get("/api/v1/intelligence/counterfeit-risk/")
        self.assertEqual(r1.status_code, status.HTTP_200_OK)
        self.assertEqual(r2.status_code, status.HTTP_200_OK)
        self.assertIn("analysis", r2.json()["data"])

    def test_supply_chain_timeline(self):
        r = self.client.get("/api/v1/traceability/supply-chain/shipments/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_recall_orchestration(self):
        r = self.client.get("/api/v1/traceability/recall-orchestration/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_pharmacy_network(self):
        r = self.client.get("/api/v1/pharmacies/network/ranking/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_crisis_mode(self):
        r = self.client.get("/api/v1/emergency-response/crisis-mode/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_analytics_export(self):
        r = self.client.get("/api/v1/analytics/export-bundle/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertTrue(r.json()["data"].get("export_ready"))

    def test_public_verified_pharmacies(self):
        r = self.client.get("/api/v1/pharmacies/network/verified/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
