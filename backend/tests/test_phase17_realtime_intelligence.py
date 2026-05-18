"""Phase 17 — realtime event bus and operational intelligence."""
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase

from apps.accounts.models import Role
from apps.core.constants import EventCategory, RoleCode
from apps.core.redis_bus import InMemoryPubSub, publish_channel
from apps.organisations.models import Organisation, OrganisationType
from apps.streambus.constants import EVT_SCAN, EVT_SCAN_SUSPICIOUS
from apps.streambus.models import EventLifecycleLog
from apps.streambus.services.bus import OperationalEventBus, publish_operational_event
from apps.streambus.services.telemetry import aggregate_telemetry
from apps.tenancy.models import OrganisationMembership

User = get_user_model()


class Phase17RealtimeIntelligenceTests(APITestCase):
    def setUp(self):
        self.reg_role, _ = Role.objects.get_or_create(code=RoleCode.NAFDAC_ADMIN, defaults={"name": "NAFDAC"})
        self.mfg_role, _ = Role.objects.get_or_create(
            code=RoleCode.MANUFACTURER_ADMIN, defaults={"name": "Mfg Admin"}
        )
        self.regulator = User.objects.create_user(
            username="reg_p17", password="pass", role=self.reg_role, is_regulator=True
        )
        ot, _ = OrganisationType.objects.get_or_create(code="manufacturer", defaults={"name": "Mfg"})
        self.org_a = Organisation.objects.create(organisation_type=ot, legal_name="Tenant A")
        self.org_b = Organisation.objects.create(organisation_type=ot, legal_name="Tenant B")
        self.user_a = User.objects.create_user(
            username="user_p17a", password="pass", role=self.mfg_role, organisation=self.org_a
        )
        OrganisationMembership.objects.create(
            user=self.user_a,
            organisation=self.org_a,
            role=self.mfg_role,
            membership_status=OrganisationMembership.STATUS_ACTIVE,
            is_primary=True,
        )

    def test_event_publishing(self):
        event = publish_operational_event(
            event_type=EVT_SCAN,
            payload={"serial": "NG-TEST-1"},
            organisation_id=self.org_a.id,
        )
        self.assertIn("event_id", event)
        self.assertTrue(EventLifecycleLog.objects.filter(event_id=event["event_id"]).exists())

    def test_tenant_event_isolation(self):
        publish_operational_event(
            event_type=EVT_SCAN,
            payload={"org": "a"},
            organisation_id=self.org_a.id,
        )
        publish_operational_event(
            event_type=EVT_SCAN,
            payload={"org": "b"},
            organisation_id=self.org_b.id,
        )
        events = OperationalEventBus.replay(organisation_id=self.org_a.id, limit=50)
        for ev in events:
            if ev.get("organisation_id"):
                self.assertEqual(ev["organisation_id"], str(self.org_a.id))

    def test_fallback_without_redis(self):
        received = []

        def handler(channel, message):
            received.append((channel, message))

        pubsub = InMemoryPubSub()
        pubsub.subscribe("test:channel", handler)
        publish_channel("test:channel", {"ok": True})
        self.assertEqual(len(received), 1)

    def test_event_replay_api(self):
        publish_operational_event(event_type=EVT_SCAN_SUSPICIOUS, payload={"test": True}, organisation_id=self.org_a.id)
        client = APIClient()
        client.force_authenticate(user=self.regulator)
        res = client.get("/api/v1/streambus/replay/")
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(res.json()["data"]["count"], 1)

    def test_telemetry_aggregation(self):
        snap = aggregate_telemetry(organisation=self.org_a)
        self.assertIsNotNone(snap.id)
        self.assertIn("scan_throughput", snap.metrics)

    def test_command_center_live(self):
        client = APIClient()
        client.force_authenticate(user=self.regulator)
        res = client.get("/api/v1/streambus/command-center/live/")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["data"]["live"])

    def test_event_acknowledge(self):
        event = publish_operational_event(event_type=EVT_SCAN, payload={}, organisation_id=self.org_a.id)
        ok = OperationalEventBus.acknowledge(event_id=event["event_id"])
        self.assertTrue(ok)
