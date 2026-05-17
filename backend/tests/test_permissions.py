from django.test import TestCase
from rest_framework.test import APIRequestFactory

from apps.accounts.models import Role, User
from apps.core.constants import RoleCode
from apps.core.permissions import IsRegulatorUser


class PermissionTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.regulator_role = Role.objects.create(
            code=RoleCode.NAFDAC_ADMIN,
            name="NAFDAC Admin",
        )

    def test_regulator_permission(self):
        user = User.objects.create_user(
            username="reg1",
            password="testpass123",
            role=self.regulator_role,
        )
        request = self.factory.get("/")
        request.user = user
        self.assertTrue(IsRegulatorUser().has_permission(request, None))
