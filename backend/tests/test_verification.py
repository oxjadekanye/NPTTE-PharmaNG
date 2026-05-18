from django.test import TestCase
from rest_framework.test import APIClient

from apps.core.constants import BatchLifecycleStatus
from apps.organisations.models import Organisation, OrganisationType
from apps.products.models import Product, ProductBatch
from apps.serialization.models import ProductSerial


class VerificationAPITests(TestCase):
    def setUp(self):
        org_type, _ = OrganisationType.objects.get_or_create(
            code="manufacturer",
            defaults={"name": "Manufacturer"},
        )
        org = Organisation.objects.create(
            organisation_type=org_type,
            legal_name="Test Mfg",
        )
        product = Product.objects.create(
            name="Test Med",
            active_ingredient="Test",
            manufacturer=org,
        )
        batch = ProductBatch.objects.create(
            product=product,
            batch_number="B001",
            regulator_status="approved",
            lifecycle_status=BatchLifecycleStatus.ACTIVE,
        )
        self.serial = ProductSerial.objects.create(
            batch=batch,
            serial_number="NG-TEST-VERIFY-001",
            qr_payload="https://verify.nptte.gov.ng/v1/NG-TEST-VERIFY-001",
        )
        self.client = APIClient()

    def test_verify_authentic_serial(self):
        response = self.client.post(
            "/api/v1/verification/authenticate/",
            {"serial_number": self.serial.serial_number},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["success"])
        self.assertTrue(body["data"]["is_authentic"])
