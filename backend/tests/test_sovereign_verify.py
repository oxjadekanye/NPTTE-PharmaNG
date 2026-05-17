from django.test import TestCase
from rest_framework.test import APIClient, APIRequestFactory

from apps.organisations.models import Organisation, OrganisationType
from apps.products.models import Product, ProductBatch
from apps.serialization.services import generate_medication_serial, issue_serials_for_batch
from apps.verification.services import sovereign_verify


class SovereignVerificationTests(TestCase):
    def setUp(self):
        org_type, _ = OrganisationType.objects.get_or_create(code="manufacturer", defaults={"name": "Mfg"})
        org = Organisation.objects.create(organisation_type=org_type, legal_name="Mfg Co")
        self.product = Product.objects.create(
            name="Paracetamol",
            active_ingredient="Paracetamol",
            manufacturer=org,
        )
        self.batch = ProductBatch.objects.create(
            product=self.product,
            batch_number="B-2026-001",
            regulator_status="approved",
        )
        self.serial = issue_serials_for_batch(batch=self.batch, count=1)[0]

    def test_nptte_serial_format(self):
        self.assertTrue(self.serial.serial_number.startswith("NG-NPTTE-"))

    def test_sovereign_verify_authentic(self):
        factory = APIRequestFactory()
        request = factory.post("/api/v1/verification/authenticate/", {"serial_number": self.serial.serial_number})
        result = sovereign_verify(request=request, serial_number=self.serial.serial_number)
        self.assertEqual(result["data"]["outcome"], "authentic")
        self.assertTrue(result["data"]["is_authentic"])

    def test_api_authenticate_endpoint(self):
        client = APIClient()
        response = client.post(
            "/api/v1/verification/authenticate/",
            {"serial_number": self.serial.serial_number},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["data"]["is_authentic"])
