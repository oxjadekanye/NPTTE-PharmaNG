"""Phase 19 — drill-down explorer API."""
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase

from apps.accounts.models import Role
from apps.core.constants import RoleCode
from apps.enforcement.models import EnforcementCase
from apps.explorer.constants import ENTITY_TYPES
from apps.organisations.models import Organisation, OrganisationType
from apps.scanning.models import ScanEvent
from apps.tenancy.models import OrganisationMembership

User = get_user_model()


class Phase19ExplorerTests(APITestCase):
    def setUp(self):
        self.reg_role, _ = Role.objects.get_or_create(code=RoleCode.NAFDAC_ADMIN, defaults={"name": "NAFDAC"})
        self.pharm_role, _ = Role.objects.get_or_create(
            code=RoleCode.PHARMACY_ADMIN, defaults={"name": "Pharmacy Admin"}
        )
        self.regulator = User.objects.create_user(
            username="reg_p19", password="pass", role=self.reg_role, is_regulator=True
        )
        ot, _ = OrganisationType.objects.get_or_create(code="pharmacy", defaults={"name": "Pharmacy"})
        self.org_a = Organisation.objects.create(organisation_type=ot, legal_name="Pharmacy A", state="Lagos")
        self.org_b = Organisation.objects.create(organisation_type=ot, legal_name="Pharmacy B", state="Kano")
        self.user_a = User.objects.create_user(
            username="pharm_a", password="pass", role=self.pharm_role, organisation=self.org_a
        )
        self.user_b = User.objects.create_user(
            username="pharm_b", password="pass", role=self.pharm_role, organisation=self.org_b
        )
        OrganisationMembership.objects.create(
            user=self.user_a,
            organisation=self.org_a,
            role=self.pharm_role,
            membership_status=OrganisationMembership.STATUS_ACTIVE,
            is_primary=True,
        )
        OrganisationMembership.objects.create(
            user=self.user_b,
            organisation=self.org_b,
            role=self.pharm_role,
            membership_status=OrganisationMembership.STATUS_ACTIVE,
            is_primary=True,
        )
        self.scan_b = ScanEvent.objects.create(
            serial_number="SN-B-001",
            scan_type=ScanEvent.SCAN_PHARMACY_DISPENSE,
            organisation=self.org_b,
            outcome_label="suspicious",
        )

    def test_explorer_resolve_aggregate_regulator(self):
        c = APIClient()
        c.force_authenticate(user=self.regulator)
        r = c.get("/api/v1/explorer/resolve/", {"type": "national_risk", "id": "national-risk-current"})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["success"])

    def test_explorer_aggregate_denied_for_org_user(self):
        c = APIClient()
        c.force_authenticate(user=self.user_a)
        r = c.get("/api/v1/explorer/detail/national_risk/national-risk-current/")
        self.assertEqual(r.status_code, 403)

    def test_explorer_products_tracked_aggregate_denied_for_org_user(self):
        c = APIClient()
        c.force_authenticate(user=self.user_a)
        r = c.get("/api/v1/explorer/detail/product_risk/products-tracked-current/")
        self.assertEqual(r.status_code, 403)

    def test_explorer_command_activity_allowed(self):
        c = APIClient()
        c.force_authenticate(user=self.user_a)
        r = c.get("/api/v1/explorer/detail/task/command-activity-current/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("records", r.json()["data"])

    def test_cross_tenant_scan_denied(self):
        c = APIClient()
        c.force_authenticate(user=self.user_a)
        r = c.get(f"/api/v1/explorer/detail/scan_event/{self.scan_b.id}/")
        self.assertEqual(r.status_code, 403)

    def test_public_enforcement_unauthorized(self):
        c = APIClient()
        case = EnforcementCase.objects.create(
            case_reference="ENF-P19-TEST",
            title="Sensitive",
            summary="",
            case_status=EnforcementCase.STATUS_OPEN,
            severity=EnforcementCase.SEV_HIGH,
        )
        r = c.get(f"/api/v1/explorer/detail/enforcement_case/{case.id}/")
        self.assertEqual(r.status_code, 401)

    def test_regulator_enforcement_detail(self):
        case = EnforcementCase.objects.create(
            case_reference="ENF-P19-REG",
            title="Case",
            summary="",
            case_status=EnforcementCase.STATUS_OPEN,
            severity=EnforcementCase.SEV_HIGH,
        )
        c = APIClient()
        c.force_authenticate(user=self.regulator)
        r = c.get(f"/api/v1/explorer/detail/enforcement_case/{case.id}/")
        self.assertEqual(r.status_code, 200)

    def test_risk_breakdown_national_aggregate(self):
        c = APIClient()
        c.force_authenticate(user=self.regulator)
        r = c.get("/api/v1/explorer/risk-breakdown/national_risk/national-risk-current/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("contributions", r.json()["data"])

    def test_related_and_timeline(self):
        c = APIClient()
        c.force_authenticate(user=self.regulator)
        r = c.get("/api/v1/explorer/related/national_risk/national-risk-current/")
        self.assertEqual(r.status_code, 200)
        r2 = c.get("/api/v1/explorer/timeline/national_risk/national-risk-current/")
        self.assertEqual(r2.status_code, 200)

    def test_invalid_entity_type(self):
        c = APIClient()
        c.force_authenticate(user=self.regulator)
        r = c.get("/api/v1/explorer/resolve/", {"type": "not_a_real_type", "id": "national-risk-current"})
        self.assertEqual(r.status_code, 400)

    def test_missing_resolve_params(self):
        c = APIClient()
        c.force_authenticate(user=self.regulator)
        r = c.get("/api/v1/explorer/resolve/", {"type": "national_risk"})
        self.assertEqual(r.status_code, 400)

    def test_execute_create_task(self):
        c = APIClient()
        c.force_authenticate(user=self.regulator)
        r = c.post(
            "/api/v1/explorer/actions/national_risk/national-risk-current/execute/",
            {"action_id": "create_task", "confirm": True, "title": "Follow-up from explorer"},
            format="json",
        )
        self.assertEqual(r.status_code, 201)

    def test_execute_denied_non_regulator(self):
        c = APIClient()
        c.force_authenticate(user=self.user_a)
        r = c.post(
            f"/api/v1/explorer/actions/scan_event/{self.scan_b.id}/execute/",
            {"action_id": "create_task", "confirm": True},
            format="json",
        )
        self.assertEqual(r.status_code, 403)

    def test_entity_types_constant(self):
        self.assertIn("national_risk", ENTITY_TYPES)
        self.assertIn("scan_event", ENTITY_TYPES)
