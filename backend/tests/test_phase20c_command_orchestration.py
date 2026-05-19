"""Phase 20C — command orchestration, geospatial, patches, investigations."""
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase

from apps.accounts.models import Role
from apps.command_orchestration.services.geospatial import build_map_markers, cluster_markers
from apps.command_orchestration.services.patches import build_event_patch, merge_patch_into_snapshot
from apps.command_orchestration.services.regional import build_regional_intelligence, list_regions
from apps.core.constants import RoleCode
from apps.enforcement.models import EnforcementCase, InvestigationNote

User = get_user_model()


class Phase20CCommandOrchestrationTests(APITestCase):
    def setUp(self):
        self.reg_role, _ = Role.objects.get_or_create(code=RoleCode.NAFDAC_ADMIN, defaults={"name": "NAFDAC"})
        self.regulator = User.objects.create_user(
            username="reg_p20c", password="pass", role=self.reg_role, is_regulator=True
        )
        self.case = EnforcementCase.objects.create(
            case_reference="ENF-P20C",
            title="Regional case",
            summary="Test",
            case_status=EnforcementCase.STATUS_OPEN,
            severity=EnforcementCase.SEV_HIGH,
        )

    def test_map_markers_operational(self):
        payload = build_map_markers(layer="operational", limit=10)
        self.assertEqual(payload["layer"], "operational")
        self.assertIn("markers", payload)

    def test_cluster_markers(self):
        markers = [
            {"id": "a", "lat": 6.5, "lng": 3.4, "layer": "operational", "risk_score": 50, "severity": "low", "status": "x", "organisation": "A", "active_incidents": 0},
            {"id": "b", "lat": 6.51, "lng": 3.41, "layer": "operational", "risk_score": 60, "severity": "low", "status": "x", "organisation": "B", "active_incidents": 0},
        ]
        clusters = cluster_markers(markers, cell_deg=1.0)
        self.assertTrue(len(clusters) <= len(markers))

    def test_regional_routing(self):
        regions = list_regions()
        self.assertGreaterEqual(len(regions), 6)
        sw = build_regional_intelligence("south_west")
        self.assertIsNotNone(sw)
        self.assertIn("Lagos", sw["states"])

    def test_patch_builder(self):
        patch = build_event_patch(
            event_type="task.updated",
            payload={"task_id": "t1", "task_status": "in_progress", "stream_channel": "officer_tasks"},
        )
        self.assertEqual(patch["scope"], "entity")

    def test_patch_merge_metric(self):
        snap = merge_patch_into_snapshot(
            {"metrics": {}},
            {"scope": "metric", "target": "national_threat", "ops": {"delta": 1}},
        )
        self.assertEqual(snap["metrics"]["national_threat"]["delta"], 1)

    def test_map_markers_api(self):
        c = APIClient()
        c.force_authenticate(user=self.regulator)
        r = c.get("/api/v1/command-orchestration/map-markers/?layer=counterfeit")
        self.assertEqual(r.status_code, 200)

    def test_command_room_snapshot(self):
        c = APIClient()
        c.force_authenticate(user=self.regulator)
        r = c.get("/api/v1/command-orchestration/command-room/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("map_markers", r.json()["data"])

    def test_investigation_room_note(self):
        c = APIClient()
        c.force_authenticate(user=self.regulator)
        r = c.post(
            f"/api/v1/command-orchestration/investigations/{self.case.id}/room/",
            {"action": "note", "body": "Field verification scheduled"},
            format="json",
        )
        self.assertEqual(r.status_code, 201)
        self.assertEqual(InvestigationNote.objects.filter(case=self.case).count(), 1)

    def test_scoped_streambus_replay(self):
        c = APIClient()
        c.force_authenticate(user=self.regulator)
        r = c.get("/api/v1/streambus/scoped-replay/?channel=investigation")
        self.assertEqual(r.status_code, 200)

    def test_non_regulator_denied_map(self):
        user = User.objects.create_user(username="org_p20c", password="pass", is_regulator=False)
        c = APIClient()
        c.force_authenticate(user=user)
        r = c.get("/api/v1/command-orchestration/map-markers/")
        self.assertEqual(r.status_code, 403)
