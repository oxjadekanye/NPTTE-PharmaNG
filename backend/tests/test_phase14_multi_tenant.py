"""Phase 14 — multi-tenant organisation infrastructure."""
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase

from apps.accounts.models import Role
from apps.core.constants import RoleCode
from apps.organisations.models import Organisation, OrganisationType
from apps.tenancy.models import OrganisationInvitation, OrganisationMembership
from apps.tenancy.services.invitations import accept_invitation, invite_user
from apps.tenancy.services.onboarding import apply_organisation_onboarding
from apps.tenancy.services.tenant import user_can_access_organisation

User = get_user_model()


class Phase14MultiTenantTests(APITestCase):
    def setUp(self):
        self.reg_role, _ = Role.objects.get_or_create(code=RoleCode.NAFDAC_ADMIN, defaults={"name": "NAFDAC"})
        self.mfg_role, _ = Role.objects.get_or_create(
            code=RoleCode.MANUFACTURER_ADMIN, defaults={"name": "Mfg Admin"}
        )
        self.regulator = User.objects.create_user(
            username="reg_p14", password="pass", role=self.reg_role, is_regulator=True
        )
        ot, _ = OrganisationType.objects.get_or_create(code="manufacturer", defaults={"name": "Mfg"})
        self.org_a = Organisation.objects.create(organisation_type=ot, legal_name="Tenant A Ltd")
        self.org_b = Organisation.objects.create(organisation_type=ot, legal_name="Tenant B Ltd")
        self.user_a = User.objects.create_user(
            username="user_a", password="pass", role=self.mfg_role, organisation=self.org_a
        )
        OrganisationMembership.objects.create(
            user=self.user_a,
            organisation=self.org_a,
            role=self.mfg_role,
            membership_status=OrganisationMembership.STATUS_ACTIVE,
            is_primary=True,
        )
        self.user_b = User.objects.create_user(
            username="user_b", password="pass", role=self.mfg_role, organisation=self.org_b
        )
        OrganisationMembership.objects.create(
            user=self.user_b,
            organisation=self.org_b,
            role=self.mfg_role,
            membership_status=OrganisationMembership.STATUS_ACTIVE,
            is_primary=True,
        )

    def test_cross_tenant_denial(self):
        self.assertFalse(user_can_access_organisation(self.user_a, self.org_b.id))

    def test_onboarding_apply_public(self):
        client = APIClient()
        res = client.post(
            "/api/v1/tenancy/onboarding/apply/",
            {
                "organisation_type": "pharmacy",
                "legal_name": "New Pharmacy Ltd",
                "license_number": "PH-NEW-1",
                "cac_number": "RC999",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 201)

    def test_regulator_approval_queue(self):
        apply_organisation_onboarding(org_type_key="manufacturer", legal_name="Queue Test Mfg")
        client = APIClient()
        client.force_authenticate(user=self.regulator)
        res = client.get("/api/v1/tenancy/regulator/approval-queue/")
        self.assertEqual(res.status_code, 200)

    def test_invitation_accept_flow(self):
        staff_role, _ = Role.objects.get_or_create(
            code=RoleCode.ORGANISATION_STAFF, defaults={"name": "Staff"}
        )
        invitee = User.objects.create_user(username="invitee", password="pass", email="invitee@test.ng")
        inv = invite_user(
            organisation=self.org_a,
            email="invitee@test.ng",
            role=staff_role,
            invited_by=self.user_a,
        )
        result = accept_invitation(token=inv.token, user=invitee)
        self.assertTrue(result["accepted"])
        self.assertTrue(
            OrganisationMembership.objects.filter(user=invitee, organisation=self.org_a).exists()
        )

    def test_organisation_dashboard_scoped(self):
        client = APIClient()
        client.force_authenticate(user=self.user_a)
        res = client.get("/api/v1/tenancy/dashboard/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["organisation_id"], str(self.org_a.id))

    def test_regulator_context_switch(self):
        client = APIClient()
        client.force_authenticate(user=self.regulator)
        res = client.post(
            "/api/v1/tenancy/context/switch/",
            {"organisation_id": str(self.org_a.id), "reason": "inspection"},
            format="json",
        )
        self.assertEqual(res.status_code, 200)

    def test_tenant_scoped_scan_history(self):
        from apps.scanning.models import ScanEvent

        ScanEvent.objects.create(
            serial_number="SCOPE-A",
            scan_type=ScanEvent.SCAN_PHARMACY_RECEIVE,
            organisation=self.org_a,
            user=self.user_a,
        )
        ScanEvent.objects.create(
            serial_number="SCOPE-B",
            scan_type=ScanEvent.SCAN_PHARMACY_RECEIVE,
            organisation=self.org_b,
            user=self.user_b,
        )
        client = APIClient()
        client.force_authenticate(user=self.user_a)
        res = client.get("/api/v1/scanning/history/")
        self.assertEqual(res.status_code, 200)
        serials = [r["serial_number"] for r in res.json()["data"]["scans"]]
        self.assertIn("SCOPE-A", serials)
        self.assertNotIn("SCOPE-B", serials)
