"""Phase 8 — national traceability engine (serialization, regulatory, verification, pharmacy)."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework.test import APIClient, APIRequestFactory

from apps.accounts.models import Role, User
from apps.core.constants import (
    BatchLifecycleStatus,
    RegulatorBatchStatus,
    RoleCode,
    SupplyChainTransactionType,
)
from apps.manufacturers.models import ManufacturerProfile, ManufacturingSite
from apps.manufacturers.services import create_national_batch, issue_batch_serials
from apps.organisations.models import Organisation, OrganisationType
from apps.products.models import Product, ProductBatch
from apps.products.services import approve_batch, issue_national_batch_recall
from apps.serialization.services import issue_serials_for_batch
from apps.traceability.models import BatchRegulatoryAudit
from apps.verification.services import sovereign_verify


class Phase8TraceabilityEngineTests(TestCase):
    def setUp(self):
        ot, _ = OrganisationType.objects.get_or_create(code="manufacturer", defaults={"name": "Mfg"})
        self.org = Organisation.objects.create(organisation_type=ot, legal_name="Test Mfg Org")
        self.profile = ManufacturerProfile.objects.create(organisation=self.org)
        self.site = ManufacturingSite.objects.create(
            manufacturer=self.profile,
            site_name="Plant 1",
            site_code="P1",
        )
        self.product = Product.objects.create(
            name="Amoxicillin",
            active_ingredient="Amoxicillin",
            manufacturer=self.org,
            national_product_code="AMOX500",
        )
        self.reg_role = Role.objects.create(code=RoleCode.NAFDAC_ADMIN, name="NAFDAC")
        self.reg_user = User.objects.create_user(
            username="reg_phase8",
            password="pass12345",
            role=self.reg_role,
            is_regulator=True,
        )

    def test_issue_batch_serials_requires_regulator_approval(self):
        batch = create_national_batch(
            product=self.product,
            batch_number="B-P8-001",
            manufacturing_site=self.site,
            quantity_produced=100,
            actor=None,
            request=None,
        )
        self.assertEqual(batch.regulator_status, RegulatorBatchStatus.PENDING)
        with self.assertRaises(ValidationError):
            issue_batch_serials(batch=batch, count=2, actor=None)

    def test_approve_then_issue_serials_and_audit(self):
        batch = create_national_batch(
            product=self.product,
            batch_number="B-P8-002",
            manufacturing_site=self.site,
            quantity_produced=50,
            actor=None,
            request=None,
        )
        approve_batch(batch=batch, actor=self.reg_user, request=None, notes="ok")
        serials = issue_batch_serials(batch=batch, count=3, actor=self.reg_user)
        self.assertEqual(len(serials), 3)
        self.assertTrue(serials[0].serial_number.startswith("NG-NPTTE-"))
        batch.refresh_from_db()
        self.assertEqual(batch.lifecycle_status, BatchLifecycleStatus.ACTIVE)
        self.assertGreaterEqual(BatchRegulatoryAudit.objects.filter(batch=batch).count(), 1)

    def test_recall_blocks_public_verify(self):
        batch = ProductBatch.objects.create(
            product=self.product,
            batch_number="B-P8-REC",
            regulator_status=RegulatorBatchStatus.APPROVED,
            lifecycle_status=BatchLifecycleStatus.ACTIVE,
            manufacturing_site=self.site,
        )
        serial = issue_serials_for_batch(batch=batch, count=1)[0]
        issue_national_batch_recall(
            batch=batch,
            actor=self.reg_user,
            request=None,
            reason="Test recall",
            issued_by_organisation=self.org,
        )
        batch.refresh_from_db()
        self.assertEqual(batch.lifecycle_status, BatchLifecycleStatus.RECALLED)
        factory = APIRequestFactory()
        req = factory.post("/api/v1/verification/authenticate/", {"serial_number": serial.serial_number})
        result = sovereign_verify(request=req, serial_number=serial.serial_number)
        self.assertEqual(result["data"]["outcome"], "recalled")

    def test_invalid_serial_verify(self):
        factory = APIRequestFactory()
        req = factory.post("/api/v1/verification/authenticate/", {"serial_number": "NG-NPTTE-NONE-2099-000000001"})
        result = sovereign_verify(request=req, serial_number="NG-NPTTE-NONE-2099-000000001")
        self.assertEqual(result["data"]["outcome"], "invalid_serial")

    def test_supply_chain_transaction_record_api(self):
        client = APIClient()
        role = Role.objects.create(code=RoleCode.MANUFACTURER, name="Mfg")
        u = User.objects.create_user(username="mfg_tx", password="pass12345", role=role, organisation=self.org)
        client.force_authenticate(user=u)
        batch = ProductBatch.objects.create(
            product=self.product,
            batch_number="B-TX",
            regulator_status=RegulatorBatchStatus.APPROVED,
            lifecycle_status=BatchLifecycleStatus.ACTIVE,
            manufacturing_site=self.site,
        )
        resp = client.post(
            "/api/v1/traceability/transactions/record/",
            {
                "transaction_type": SupplyChainTransactionType.MANUFACTURER_DISPATCH,
                "source_organisation_id": str(self.org.id),
                "product_id": str(self.product.id),
                "batch_id": str(batch.id),
                "quantity_delta": -10,
                "notes": "Phase 8 test dispatch",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)

    def test_pharmacy_dispense_requires_custody(self):
        from apps.pharmacies.traceability_services import pharmacy_dispense_serial

        batch = ProductBatch.objects.create(
            product=self.product,
            batch_number="B-PH",
            regulator_status=RegulatorBatchStatus.APPROVED,
            lifecycle_status=BatchLifecycleStatus.ACTIVE,
            manufacturing_site=self.site,
        )
        serial = issue_serials_for_batch(batch=batch, count=1)[0]
        role = Role.objects.create(code=RoleCode.PHARMACY_ADMIN, name="Pharm")
        pharm_org = Organisation.objects.create(
            organisation_type=OrganisationType.objects.get_or_create(code="pharmacy", defaults={"name": "Ph"})[0],
            legal_name="Test Pharmacy",
        )
        user = User.objects.create_user(
            username="pharm_p8",
            password="pass12345",
            role=role,
            organisation=pharm_org,
        )
        with self.assertRaises(ValidationError):
            pharmacy_dispense_serial(
                actor=user,
                organisation_id=pharm_org.id,
                serial_number=serial.serial_number,
                request=None,
            )

    def test_regulator_reject_creates_rejected_status(self):
        batch = create_national_batch(
            product=self.product,
            batch_number="B-P8-RJ",
            manufacturing_site=self.site,
            quantity_produced=10,
            actor=None,
            request=None,
        )
        client = APIClient()
        client.force_authenticate(user=self.reg_user)
        resp = client.post(
            f"/api/v1/regulatory/batches/{batch.id}/reject/",
            {"reason": "Incomplete documentation"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        batch.refresh_from_db()
        self.assertEqual(batch.regulator_status, RegulatorBatchStatus.REJECTED)

    def test_recall_affected_endpoint(self):
        batch = ProductBatch.objects.create(
            product=self.product,
            batch_number="B-AFF",
            regulator_status=RegulatorBatchStatus.APPROVED,
            lifecycle_status=BatchLifecycleStatus.ACTIVE,
            manufacturing_site=self.site,
        )
        client = APIClient()
        client.force_authenticate(user=self.reg_user)
        resp = client.get(f"/api/v1/regulatory/batches/recall-affected/?batch_id={batch.id}")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("pharmacy_organisation_ids", resp.json()["data"])
