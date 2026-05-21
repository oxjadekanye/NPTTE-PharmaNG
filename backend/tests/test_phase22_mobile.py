"""Phase 22 — mobile device trust, evidence, audit, realtime, copilot."""
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase

from apps.accounts.models import Role
from apps.core.constants import RoleCode
from apps.mobile.models import DeviceRegistration, MobileFieldEvidence, MobileOperationalAudit

User = get_user_model()


class Phase22MobileTests(APITestCase):
    def setUp(self):
        self.reg_role, _ = Role.objects.get_or_create(
            code=RoleCode.NAFDAC_ADMIN, defaults={"name": "NAFDAC"}
        )
        self.regulator = User.objects.create_user(
            username="reg_p22",
            password="pass",
            role=self.reg_role,
            is_regulator=True,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.regulator)
        self.device_id = "test-device-p22"

    def test_device_trust_register(self):
        res = self.client.post(
            "/api/v1/mobile/devices/trust/",
            {
                "device_id": self.device_id,
                "fingerprint": "model|ios|17|app",
                "platform": "ios",
                "app_version": "0.1.0",
                "biometric_capable": True,
            },
            format="json",
        )
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertTrue(body["success"])
        self.assertIn("trusted_status", body["data"])
        device = DeviceRegistration.objects.get(device_id=self.device_id)
        self.assertTrue(device.biometric_capable)
        self.assertTrue(
            MobileOperationalAudit.objects.filter(action_type="device.trust.register").exists()
        )

    def test_device_heartbeat(self):
        DeviceRegistration.objects.create(
            device_id=self.device_id,
            device_type="ios",
            created_by=self.regulator,
        )
        res = self.client.post(
            "/api/v1/mobile/devices/heartbeat/",
            {"device_id": self.device_id, "app_version": "0.1.1"},
            format="json",
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["data"]["ok"])

    def test_field_evidence_capture(self):
        DeviceRegistration.objects.create(
            device_id=self.device_id,
            device_type="android",
            created_by=self.regulator,
        )
        res = self.client.post(
            "/api/v1/mobile/evidence/",
            {
                "device_id": self.device_id,
                "evidence_type": "inspection",
                "notes": "Field photo",
                "photos": [{"id": "p1", "mime": "image/jpeg", "base64": "abc"}],
            },
            format="json",
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(MobileFieldEvidence.objects.count(), 1)

    def test_audit_timeline(self):
        MobileOperationalAudit.objects.create(
            actor=self.regulator,
            action_type="scan.submit",
            payload={"serial": "X"},
            created_by=self.regulator,
        )
        res = self.client.get("/api/v1/mobile/audit/timeline/")
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(len(res.json()["data"]["timeline"]), 1)

    def test_mobile_realtime_feed(self):
        res = self.client.get("/api/v1/mobile/realtime/feed/?channel=officer_tasks")
        self.assertEqual(res.status_code, 200)
        self.assertIn("events", res.json()["data"])

    def test_mobile_copilot_regulator(self):
        res = self.client.post(
            "/api/v1/mobile/copilot/",
            {"prompt_mode": "explain_risk", "user_question": "Explain scan risk"},
            format="json",
        )
        self.assertIn(res.status_code, (200, 403))

    def test_mobile_inspection_copilot_context(self):
        res = self.client.post(
            "/api/v1/mobile/copilot/",
            {
                "prompt_mode": "operational_recommendations",
                "inspection_context": {
                    "compliance_score": 30,
                    "site_passed": False,
                    "product_passed": False,
                    "compliance_passed": False,
                    "failed_items": ["Compliance: Cold-chain logs"],
                    "evidence_count": 0,
                },
            },
            format="json",
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()["data"]
        self.assertIn("risk_rating", data)
        self.assertIn("immediate_concerns", data)
        self.assertTrue(data.get("escalation_required"))
