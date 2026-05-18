"""Phase 13 — traceability demo seed, story API, verification, cleanup."""
from django.test import TestCase
from rest_framework.test import APIClient, APIRequestFactory

from apps.products.models import Product, ProductBatch
from apps.serialization.models import ProductSerial
from apps.traceability_demo.clear import clear_traceability_demo
from apps.traceability_demo.constants import (
    DEMO_TYPE,
    SERIAL_AUTHENTIC,
    SERIAL_INVALID,
    SERIAL_RECALLED,
)
from apps.traceability_demo.seed import seed_traceability_demo
from apps.verification.services import sovereign_verify


class Phase13TraceabilityDemoTests(TestCase):
    def test_seed_idempotent(self):
        first = seed_traceability_demo()
        self.assertEqual(first["status"], "seeded")
        count_after_first = Product.objects.filter(metadata__demo_type=DEMO_TYPE).count()
        second = seed_traceability_demo()
        self.assertEqual(second["status"], "already_seeded")
        self.assertEqual(Product.objects.filter(metadata__demo_type=DEMO_TYPE).count(), count_after_first)

    def test_demo_story_endpoint(self):
        seed_traceability_demo()
        client = APIClient()
        res = client.get("/api/v1/demo/traceability-story/")
        self.assertEqual(res.status_code, 200)
        data = res.json()["data"]
        self.assertTrue(data["seeded"])
        self.assertEqual(data["hero_serial"], SERIAL_AUTHENTIC)

    def test_authentic_serial_verification(self):
        seed_traceability_demo()
        factory = APIRequestFactory()
        req = factory.post("/api/v1/verification/authenticate/", {"serial_number": SERIAL_AUTHENTIC})
        result = sovereign_verify(request=req, serial_number=SERIAL_AUTHENTIC)
        self.assertEqual(result["data"]["outcome"], "authentic")

    def test_recalled_serial_verification(self):
        seed_traceability_demo()
        factory = APIRequestFactory()
        req = factory.post("/api/v1/verification/authenticate/", {"serial_number": SERIAL_RECALLED})
        result = sovereign_verify(request=req, serial_number=SERIAL_RECALLED)
        self.assertEqual(result["data"]["outcome"], "recalled")

    def test_cleanup_safety(self):
        seed_traceability_demo()
        safe = Product.objects.create(
            name="Production Medicine",
            active_ingredient="Safe",
            national_product_code="PROD-SAFE-001",
            metadata={"environment": "production"},
        )
        clear_traceability_demo()
        self.assertFalse(ProductSerial.objects.filter(serial_number=SERIAL_AUTHENTIC).exists())
        self.assertTrue(Product.objects.filter(pk=safe.pk).exists())
        self.assertEqual(Product.objects.filter(metadata__demo_type=DEMO_TYPE).count(), 0)

    def test_invalid_serial_verification(self):
        seed_traceability_demo()
        factory = APIRequestFactory()
        req = factory.post("/api/v1/verification/authenticate/", {"serial_number": SERIAL_INVALID})
        result = sovereign_verify(request=req, serial_number=SERIAL_INVALID)
        self.assertEqual(result["data"]["outcome"], "invalid_serial")
