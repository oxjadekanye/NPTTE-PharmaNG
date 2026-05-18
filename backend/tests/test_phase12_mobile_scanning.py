"""Phase 12 — mobile scanning ingest and ScanEvent ledger."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.scanning.models import ScanEvent

User = get_user_model()


class Phase12ScanningTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="pharmacy_scanner",
            email="scan@test.ng",
            password="test-pass-12",
        )

    def test_citizen_scan_ingest_public(self):
        res = self.client.post(
            "/api/v1/scanning/ingest/",
            {
                "serial_number": "UNKNOWN-SERIAL-PH12",
                "scan_type": ScanEvent.SCAN_CITIZEN,
                "actor_role": "citizen",
                "device_id": "citizen-device-1",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 201)
        body = res.json()
        self.assertTrue(body["success"])
        self.assertIn("outcome_label", body["data"])
        self.assertEqual(ScanEvent.objects.count(), 1)

    def test_pharmacy_scan_requires_auth(self):
        res = self.client.post(
            "/api/v1/scanning/ingest/",
            {
                "serial_number": "RX-001",
                "scan_type": ScanEvent.SCAN_PHARMACY_RECEIVE,
                "actor_role": "pharmacy",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 401)

    def test_pharmacy_scan_authenticated(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.post(
            "/api/v1/scanning/ingest/",
            {
                "serial_number": "RX-002",
                "scan_type": ScanEvent.SCAN_PHARMACY_RECEIVE,
                "actor_role": "pharmacy",
                "device_id": "pharm-tab-1",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 201)
        event = ScanEvent.objects.latest("created_at")
        self.assertEqual(event.scan_type, ScanEvent.SCAN_PHARMACY_RECEIVE)
        self.assertIn("alerts", res.json()["data"])

    def test_offline_pending_sync(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.post(
            "/api/v1/scanning/ingest/",
            {
                "serial_number": "OFFLINE-001",
                "scan_type": ScanEvent.SCAN_WAREHOUSE,
                "actor_role": "warehouse",
                "sync_status": ScanEvent.SYNC_PENDING,
                "offline_timestamp": "2026-05-18T10:00:00Z",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json()["data"]["sync_status"], ScanEvent.SYNC_PENDING)
        self.assertEqual(res.json()["data"]["outcome_label"], "queued")

    def test_scan_history(self):
        self.client.force_authenticate(user=self.user)
        ScanEvent.objects.create(
            serial_number="HIST-1",
            scan_type=ScanEvent.SCAN_CITIZEN,
            actor_role="citizen",
            user=self.user,
            outcome_label="authentic",
        )
        res = self.client.get("/api/v1/scanning/history/")
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(res.json()["data"]["count"], 1)
