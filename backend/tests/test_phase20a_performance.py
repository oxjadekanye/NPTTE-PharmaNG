"""Phase 20A — explorer cache, context routing, overview payloads."""
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient, APITestCase

from apps.accounts.models import Role
from apps.core.constants import RoleCode
from apps.explorer.services.cache import PREFIX, cached_explorer
from apps.explorer.services.context_router import resolve_context_route
from apps.explorer.services.invalidate import on_streambus_event

User = get_user_model()


class Phase20AExplorerTests(APITestCase):
    def setUp(self):
        self.reg_role, _ = Role.objects.get_or_create(code=RoleCode.NAFDAC_ADMIN, defaults={"name": "NAFDAC"})
        self.regulator = User.objects.create_user(
            username="reg_p20a", password="pass", role=self.reg_role, is_regulator=True
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.regulator)
        cache.clear()

    def test_context_route_returns_entity(self):
        route = resolve_context_route(context_key="national_status", user=self.regulator)
        self.assertIn("entity_type", route)
        self.assertIn("entity_id", route)

    def test_context_route_api(self):
        r = self.client.get("/api/v1/explorer/context-route/", {"context": "counterfeit_detections"})
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertTrue(body["success"])
        self.assertIn(body["data"]["entity_type"], ("counterfeit_cluster", "intelligence_signal", "national_risk"))

    def test_overview_endpoint(self):
        route = resolve_context_route(context_key="open_alerts", user=self.regulator)
        r = self.client.get(
            f"/api/v1/explorer/overview/{route['entity_type']}/{route['entity_id']}/"
        )
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["success"])
        self.assertIn("summary", r.json()["data"])

    def test_timeline_pagination_shape(self):
        r = self.client.get("/api/v1/explorer/timeline/national_risk/national-risk-current/?page=1&page_size=5")
        self.assertEqual(r.status_code, 200)
        timeline = r.json()["data"]["timeline"]
        self.assertIn("items", timeline)
        self.assertIn("has_more", timeline)

    def test_cached_explorer_roundtrip(self):
        calls = {"n": 0}

        def builder():
            calls["n"] += 1
            return {"ok": True}

        v1 = cached_explorer(
            scope="overview",
            entity_type="national_risk",
            entity_id="national-risk-current",
            user_id=str(self.regulator.pk),
            ttl=30,
            builder=builder,
        )
        v2 = cached_explorer(
            scope="overview",
            entity_type="national_risk",
            entity_id="national-risk-current",
            user_id=str(self.regulator.pk),
            ttl=30,
            builder=builder,
        )
        self.assertEqual(v1, v2)
        self.assertEqual(calls["n"], 1)
        self.assertTrue(PREFIX.startswith("nptte:explorer"))

    def test_streambus_invalidation_does_not_raise(self):
        on_streambus_event(event_type="scan.created", payload={})
