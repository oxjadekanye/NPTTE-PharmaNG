"""Phase 10 — sovereign serialization, intelligence, custody, certificates."""
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from apps.accounts.models import Role
from apps.core.constants import RoleCode
from apps.serialization.gs1 import build_gs1_element_string, decode_gs1_scan, resolve_serial_from_scan

User = get_user_model()


class Phase10Gs1Tests(APITestCase):
    def test_decode_nptte_serial(self):
        decoded = decode_gs1_scan("NG-NPTTE-PARACETAMOL-2026-000000001")
        self.assertEqual(decoded.national_serial, "NG-NPTTE-PARACETAMOL-2026-000000001")
        self.assertEqual(resolve_serial_from_scan(decoded.raw), decoded.national_serial)

    def test_build_gs1_element_string(self):
        el = build_gs1_element_string(gtin="1234567890123", serial="NG-NPTTE-TEST-1")
        self.assertTrue(el.startswith("01"))
        self.assertIn("21", el)


class Phase10ApiSmokeTests(APITestCase):
    def setUp(self):
        role, _ = Role.objects.get_or_create(code=RoleCode.NAFDAC_ADMIN, defaults={"name": "NAFDAC"})
        self.user = User.objects.create_user(
            username="p10_regulator",
            email="p10@test.ng",
            password="TestPass2026!",
            role=role,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_serialization_dashboard(self):
        r = self.client.get("/api/v1/serialization/dashboard/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_intelligence_national(self):
        r = self.client.get("/api/v1/intelligence/national/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn("national_risk_score", r.json()["data"])

    def test_developer_overview(self):
        r = self.client.get("/api/v1/developer/overview/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_custody_timeline_requires_serial(self):
        r = self.client.get("/api/v1/traceability/custody/timeline/")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
