"""
DRF permission classes for NPTTE role-based API access.
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.core.constants import RoleCode
from apps.core.roles import get_user_role_code, is_pharmacy_staff, is_regulator_user


class IsRegulatorUser(BasePermission):
    """NAFDAC, NDLEA, auditor, or super admin."""

    message = "Regulator or auditor access required."

    def has_permission(self, request, view):
        return is_regulator_user(request.user)


class IsPharmacyStaff(BasePermission):
    """Pharmacy admin or pharmacist with organisation membership."""

    message = "Pharmacy staff access required."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        if not is_pharmacy_staff(user):
            return False
        return bool(user.organisation_id)


class IsPharmacyInventoryManager(BasePermission):
    """Pharmacy staff who may modify inventory (not read-only)."""

    message = "Pharmacy inventory management access required."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return IsPharmacyStaff().has_permission(request, view)
        user = request.user
        if user.is_superuser:
            return True
        code = get_user_role_code(user)
        return code in RoleCode.PHARMACY_CODES and bool(user.organisation_id)


class IsPatientUser(BasePermission):
    """Authenticated patient role."""

    message = "Patient access required."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        return get_user_role_code(user) == RoleCode.PATIENT


class IsPatientOrReadOnly(BasePermission):
    """Patients: read-only on shared resources; staff have full access."""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or is_regulator_user(user):
            return True
        if get_user_role_code(user) == RoleCode.PATIENT:
            return request.method in SAFE_METHODS
        return True


class IsOrganisationMember(BasePermission):
    """User must belong to an organisation (or be staff/regulator)."""

    message = "Organisation membership required."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or is_regulator_user(user):
            return True
        return bool(user.organisation_id)


class IsPharmacyStaffOrRegulator(BasePermission):
    """Pharmacy staff or regulator (read pharmacy data)."""

    def has_permission(self, request, view):
        return IsPharmacyStaff().has_permission(request, view) or IsRegulatorUser().has_permission(
            request, view
        )


class IsSuperAdmin(BasePermission):
    message = "Super administrator access required."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.is_superuser or get_user_role_code(user) == RoleCode.SUPER_ADMIN
