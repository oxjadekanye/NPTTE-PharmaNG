"""Role resolution helpers for API permissions."""
from __future__ import annotations
from apps.core.constants import RoleCode


def get_user_role_code(user) -> str | None:
    if not user or not user.is_authenticated:
        return None
    if user.is_superuser:
        return RoleCode.SUPER_ADMIN
    if user.role_id and user.role:
        return user.role.code
    return None


def user_has_role(user, *codes: str) -> bool:
    role_code = get_user_role_code(user)
    return role_code in codes if role_code else False


def is_regulator_user(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser or getattr(user, "is_regulator", False):
        return True
    return user_has_role(
        user,
        RoleCode.SUPER_ADMIN,
        RoleCode.NAFDAC_ADMIN,
        RoleCode.NDLEA_ADMIN,
        RoleCode.AUDITOR,
        RoleCode.NATIONAL_REGULATOR,
        RoleCode.STATE_REGULATOR,
        RoleCode.PCN_ADMIN,
        RoleCode.NHIA_ADMIN,
        RoleCode.FMOH_ADMIN,
    )


def is_pharmacy_staff(user) -> bool:
    return user_has_role(user, RoleCode.PHARMACY_ADMIN, RoleCode.PHARMACIST) or user.is_staff


def is_patient_user(user) -> bool:
    return user_has_role(user, RoleCode.PATIENT)


def sync_regulator_flag(user) -> None:
    """Align is_regulator with role code (call before save)."""
    role_code = None
    if user.role_id and user.role:
        role_code = user.role.code
    user.is_regulator = role_code in RoleCode.REGULATOR_CODES or user.is_superuser
