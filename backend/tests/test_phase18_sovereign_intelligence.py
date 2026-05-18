"""Phase 18 — sovereign intelligence and enforcement."""
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase

from apps.accounts.models import Role
from apps.core.constants import RoleCode
from apps.enforcement.models import EnforcementCase, EnforcementRecommendation
from apps.intelligence.models import CounterfeitCluster, IntelligenceSignal
from apps.intelligence.services.correlation import run_correlation
from apps.intelligence.services.narratives import generate_narrative
from apps.intelligence.services.scoring import (
    calculate_national_risk,
    calculate_organisation_risk,
    calculate_product_risk,
    calculate_regional_risk,
)
from apps.organisations.models import Organisation, OrganisationType
from apps.products.models import Product
from apps.tenancy.models import OrganisationMembership

User = get_user_model()


class Phase18SovereignIntelligenceTests(APITestCase):
    def setUp(self):
        self.reg_role, _ = Role.objects.get_or_create(code=RoleCode.NAFDAC_ADMIN, defaults={"name": "NAFDAC"})
        self.mfg_role, _ = Role.objects.get_or_create(
            code=RoleCode.MANUFACTURER_ADMIN, defaults={"name": "Mfg Admin"}
        )
        self.regulator = User.objects.create_user(
            username="reg_p18", password="pass", role=self.reg_role, is_regulator=True
        )
        ot, _ = OrganisationType.objects.get_or_create(code="manufacturer", defaults={"name": "Mfg"})
        self.org = Organisation.objects.create(organisation_type=ot, legal_name="Org P18", state="Lagos")
        self.user_org = User.objects.create_user(
            username="user_p18", password="pass", role=self.mfg_role, organisation=self.org
        )
        OrganisationMembership.objects.create(
            user=self.user_org,
            organisation=self.org,
            role=self.mfg_role,
            membership_status=OrganisationMembership.STATUS_ACTIVE,
            is_primary=True,
        )
        self.product = Product.objects.create(name="Test Drug", active_ingredient="API", manufacturer=self.org)

    def test_national_risk_scoring(self):
        risk = calculate_national_risk()
        self.assertIn(risk["status"], ("green", "amber", "red", "critical"))
        self.assertGreaterEqual(risk["score"], 0)

    def test_organisation_risk_scoring(self):
        risk = calculate_organisation_risk(organisation=self.org)
        self.assertIn("reasons", risk)

    def test_product_risk_scoring(self):
        risk = calculate_product_risk(product=self.product)
        self.assertIn("counterfeit_probability", risk)

    def test_regional_risk_scoring(self):
        risk = calculate_regional_risk(region_state="Lagos")
        self.assertIn("score", risk)

    def test_correlation_signal_creation(self):
        result = run_correlation(window_hours=720, suspicious_threshold=1)
        self.assertIn("signals_created", result)

    def test_narrative_generation(self):
        from apps.intelligence.models import IntelligenceNarrative

        n = generate_narrative(narrative_type=IntelligenceNarrative.NARRATIVE_EXECUTIVE)
        self.assertTrue(len(n.body) > 20)

    def test_regulator_national_risk_api(self):
        client = APIClient()
        client.force_authenticate(user=self.regulator)
        res = client.get("/api/v1/intelligence/national-risk/")
        self.assertEqual(res.status_code, 200)

    def test_tenant_organisation_risk(self):
        client = APIClient()
        client.force_authenticate(user=self.user_org)
        res = client.get(f"/api/v1/intelligence/organisation-risk/?organisation_id={self.org.id}")
        self.assertEqual(res.status_code, 200)

    def test_tenant_denied_national_risk(self):
        client = APIClient()
        client.force_authenticate(user=self.user_org)
        res = client.get("/api/v1/intelligence/national-risk/")
        self.assertEqual(res.status_code, 403)

    def test_enforcement_recommendation_flow(self):
        client = APIClient()
        client.force_authenticate(user=self.regulator)
        res = client.get("/api/v1/intelligence/national-risk/")
        self.assertEqual(res.status_code, 200)
        recs = EnforcementRecommendation.objects.all()
        if recs.exists():
            rec = recs.first()
            accept = client.post(f"/api/v1/enforcement/recommendations/{rec.id}/accept/")
            self.assertEqual(accept.status_code, 200)

    def test_enforcement_case_creation(self):
        client = APIClient()
        client.force_authenticate(user=self.regulator)
        res = client.post(
            "/api/v1/enforcement/cases/",
            {"title": "Test case", "severity": "high", "organisation_id": str(self.org.id)},
            format="json",
        )
        self.assertEqual(res.status_code, 201)
        self.assertTrue(EnforcementCase.objects.filter(title="Test case").exists())

    def test_legacy_intelligence_routes_preserved(self):
        client = APIClient()
        client.force_authenticate(user=self.regulator)
        res = client.get("/api/v1/intelligence/national/")
        self.assertEqual(res.status_code, 200)

    def test_streambus_publish_fallback(self):
        from unittest.mock import patch

        from apps.intelligence.services.events import publish_intelligence_event

        with patch("apps.streambus.services.bus.publish_operational_event", side_effect=RuntimeError("offline")):
            publish_intelligence_event("intelligence.signal.created", {"signal_id": "test"})
