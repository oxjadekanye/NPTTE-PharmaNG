from apps.core.constants import RoleCode
from apps.core.permissions import IsOrganisationMember
from apps.core.roles import get_user_role_code


class IsManufacturerStaff(IsOrganisationMember):
    message = "Manufacturer organisation membership required."

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        code = get_user_role_code(request.user)
        return code in {RoleCode.MANUFACTURER, RoleCode.SUPER_ADMIN} or request.user.is_superuser
