"""Regression tests for /api/v1/public/verify/ — citizen demo serials must not 500."""
from rest_framework.test import APIClient, APITestCase

from apps.traceability_demo.constants import (
    SERIAL_AUTHENTIC,
    SERIAL_EXPIRED,
    SERIAL_INVALID,
    SERIAL_RECALLED,
    SERIAL_SUSPICIOUS,
)
from apps.traceability_demo.seed import seed_traceability_demo


class PublicVerifyRegressionTests(APITestCase):
    def setUp(self):
        seed_traceability_demo()
        self.client = APIClient()

    def _verify(self, serial: str):
        return self.client.post("/api/v1/public/verify/", {"serial_number": serial}, format="json")

    def test_authentic_demo_serial(self):
        res = self._verify(SERIAL_AUTHENTIC)
        self.assertLess(res.status_code, 500)
        self.assertEqual(res.json()["data"]["outcome"], "authentic")

    def test_recalled_demo_serial(self):
        res = self._verify(SERIAL_RECALLED)
        self.assertLess(res.status_code, 500)
        self.assertEqual(res.json()["data"]["outcome"], "recalled")

    def test_suspicious_demo_serial(self):
        res = self._verify(SERIAL_SUSPICIOUS)
        self.assertLess(res.status_code, 500)
        self.assertEqual(res.json()["data"]["outcome"], "counterfeit_suspected")

    def test_expired_demo_serial(self):
        res = self._verify(SERIAL_EXPIRED)
        self.assertLess(res.status_code, 500)
        self.assertEqual(res.json()["data"]["outcome"], "expired")

    def test_invalid_demo_serial(self):
        res = self._verify(SERIAL_INVALID)
        self.assertLess(res.status_code, 500)
        self.assertEqual(res.json()["data"]["outcome"], "invalid_serial")

    def test_matches_verification_authenticate_outcome(self):
        """Public verify uses same sovereign_verify engine as /verification/authenticate/."""
        pub = self._verify(SERIAL_AUTHENTIC).json()["data"]["outcome"]
        auth = self.client.post(
            "/api/v1/verification/authenticate/",
            {"serial_number": SERIAL_AUTHENTIC},
            format="json",
        ).json()["data"]["outcome"]
        self.assertEqual(pub, auth)
