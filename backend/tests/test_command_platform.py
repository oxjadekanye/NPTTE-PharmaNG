"""Phase 5 national command platform smoke tests."""
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from apps.accounts.models import Role
from apps.core.constants import RoleCode
from apps.events.services import EventStreamService
from apps.core.constants import EventCategory

User = get_user_model()


class CommandPlatformTests(APITestCase):
    def setUp(self):
        role, _ = Role.objects.get_or_create(code=RoleCode.NAFDAC_ADMIN, defaults={"name": "NAFDAC"})
        self.regulator = User.objects.create_user(
            username="cmd_regulator",
            email="cmd@test.ng",
            password="TestPass2026!",
            role=role,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.regulator)

    def test_health_unchanged(self):
        response = APIClient().get("/api/v1/health/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_command_center_live_overview(self):
        response = self.client.get("/api/v1/command-center/live-overview/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["success"])

    def test_public_verify_requires_payload(self):
        response = APIClient().post("/api/v1/public/verify/", {}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_event_publish_and_replay(self):
        EventStreamService.publish_event(
            category=EventCategory.SYSTEM,
            event_type="test_event",
            payload={"test": True},
        )
        events = EventStreamService.consume_event(category=EventCategory.SYSTEM, limit=5)
        self.assertTrue(len(events) >= 1)

    def test_analytics_national_summary(self):
        response = self.client.get("/api/v1/analytics/national-summary/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
