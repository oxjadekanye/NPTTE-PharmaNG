from django.test import TestCase

from apps.accounts.models import Role
from apps.core.constants import RoleCode, SupplyChainTransactionType
from apps.organisations.models import Organisation, OrganisationType
from apps.traceability.services import record_supply_chain_transaction


class TraceabilityEngineTests(TestCase):
    def setUp(self):
        org_type, _ = OrganisationType.objects.get_or_create(
            code="pharmacy",
            defaults={"name": "Pharmacy"},
        )
        self.org = Organisation.objects.create(
            organisation_type=org_type,
            legal_name="Test Pharmacy",
        )

    def test_record_transaction_creates_immutable_audit_reference(self):
        txn = record_supply_chain_transaction(
            transaction_type=SupplyChainTransactionType.PHARMACY_STOCKING,
            destination_organisation=self.org,
            quantity_delta=10,
        )
        self.assertTrue(txn.is_immutable)
        self.assertIsNotNone(txn.audit_reference)
        self.assertEqual(txn.transaction_type, SupplyChainTransactionType.PHARMACY_STOCKING)
