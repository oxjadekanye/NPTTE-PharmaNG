"""Phase 5 API smoke tests — additive routes only."""
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from apps.accounts.models import Role
from apps.core.constants import RegulatorBatchStatus, RoleCode
from apps.organisations.models import Organisation, OrganisationType
from apps.products.models import Product, ProductBatch

User = get_user_model()


class Phase5APITests(APITestCase):
    def setUp(self):
        role, _ = Role.objects.get_or_create(code=RoleCode.NAFDAC_ADMIN, defaults={"name": "NAFDAC"})
        self.regulator = User.objects.create_user(
            username="regulator_phase5",
            email="regulator_phase5@test.ng",
            password="TestPass2026!",
            role=role,
        )
        self.regulator_client = APIClient()
        self.regulator_client.force_authenticate(user=self.regulator)

    def test_health_unchanged(self):
        response = APIClient().get("/api/v1/health/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_regulatory_pending_batches(self):
        response = self.regulator_client.get("/api/v1/regulatory/batches/pending/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_batch_approve_endpoint(self):
        org_type, _ = OrganisationType.objects.get_or_create(code="manufacturer", defaults={"name": "Mfg"})
        org = Organisation.objects.create(organisation_type=org_type, legal_name="Approve Test Mfg")
        product = Product.objects.create(name="Test Med", active_ingredient="Test", manufacturer=org)
        batch = ProductBatch.objects.create(
            product=product,
            batch_number="P5-BATCH-001",
            regulator_status=RegulatorBatchStatus.PENDING,
        )
        response = self.regulator_client.post(
            f"/api/v1/regulatory/batches/{batch.id}/approve/",
            {"notes": "Approved for test"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        batch.refresh_from_db()
        self.assertEqual(batch.regulator_status, RegulatorBatchStatus.APPROVED)

    def test_distributors_requires_auth(self):
        response = APIClient().get("/api/v1/distributors/warehouses/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_prescriptions_requires_auth(self):
        response = APIClient().get("/api/v1/prescriptions/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
