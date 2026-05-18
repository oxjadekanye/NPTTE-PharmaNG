"""Account and authentication API views."""
from __future__ import annotations
from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from apps.accounts.api.serializers import (
    CustomTokenObtainPairSerializer,
    PasswordChangeSerializer,
    PermissionsSerializer,
    RegisterSerializer,
    UserSerializer,
)
from apps.audit.services import log_api_action
from apps.core.api.mixins import AuditLogViewMixin
from apps.core.constants import RoleCode
from apps.core.roles import get_user_role_code

User = get_user_model()


def _role_permissions(role_code: str | None) -> list[str]:
    if not role_code:
        return []
    mapping = {
        RoleCode.SUPER_ADMIN: [
            "admin.all",
            "regulatory.all",
            "pharmacy.all",
            "patient.all",
            "audit.read",
        ],
        RoleCode.NAFDAC_ADMIN: ["regulatory.read", "regulatory.write", "audit.read"],
        RoleCode.NDLEA_ADMIN: ["regulatory.read", "regulatory.write", "audit.read"],
        RoleCode.AUDITOR: ["audit.read", "regulatory.read"],
        RoleCode.PHARMACY_ADMIN: [
            "pharmacy.profile",
            "pharmacy.inventory.read",
            "pharmacy.inventory.write",
        ],
        RoleCode.PHARMACIST: [
            "pharmacy.profile.read",
            "pharmacy.inventory.read",
            "pharmacy.inventory.write",
        ],
        RoleCode.HOSPITAL_ADMIN: ["hospital.profile", "patient.read"],
        RoleCode.DOCTOR: ["hospital.read", "patient.read"],
        RoleCode.DISTRIBUTOR: ["supply_chain.read", "supply_chain.write"],
        RoleCode.MANUFACTURER: ["supply_chain.read", "supply_chain.write"],
        RoleCode.LOGISTICS: ["logistics.read", "logistics.write"],
        RoleCode.PATIENT: [
            "patient.profile",
            "patient.medication_search",
            "patient.search_history",
        ],
        RoleCode.MANUFACTURER_ADMIN: ["supply_chain.read", "supply_chain.write", "organisation.admin"],
        RoleCode.DISTRIBUTOR_ADMIN: ["supply_chain.read", "supply_chain.write", "organisation.admin"],
        RoleCode.WAREHOUSE_ADMIN: ["logistics.read", "logistics.write", "organisation.admin"],
        RoleCode.CUSTOMS_ADMIN: ["customs.read", "customs.write", "organisation.admin"],
        RoleCode.ORGANISATION_STAFF: ["organisation.read"],
        RoleCode.WAREHOUSE_MANAGER: ["logistics.read", "logistics.write"],
        RoleCode.NATIONAL_REGULATOR: ["regulatory.read", "regulatory.write", "audit.read"],
        RoleCode.STATE_REGULATOR: ["regulatory.read", "regulatory.write", "audit.read"],
    }
    return mapping.get(role_code, [])


class RegisterView(AuditLogViewMixin, generics.CreateAPIView):
    audit_entity_type = "user"
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        log_api_action(
            request=self.request,
            action="auth.register",
            entity_type="user",
            entity_id=user.id,
            after_state={"username": user.username, "role_code": user.role_code},
        )


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]
    throttle_classes = []  # set in __init_subclass via get_throttles

    def get_throttles(self):
        from apps.core.throttling import AuthEndpointThrottle

        return [AuthEndpointThrottle()]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            log_api_action(
                request=request,
                action="auth.login",
                entity_type="user",
                after_state={"username": request.data.get("username", "")},
            )
        return response


class RefreshTokenView(TokenRefreshView):
    permission_classes = [AllowAny]


class VerifyTokenView(TokenVerifyView):
    permission_classes = [AllowAny]


class LogoutView(APIView):
    """Blacklist refresh token on logout."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response(
                {"detail": "Invalid or expired refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        log_api_action(
            request=request,
            action="auth.logout",
            entity_type="user",
            entity_id=request.user.id,
        )
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save(update_fields=["password"])
        log_api_action(
            request=request,
            action="auth.password_change",
            entity_type="user",
            entity_id=request.user.id,
        )
        return Response({"detail": "Password updated successfully."})


class PermissionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role_code = get_user_role_code(user)
        from apps.tenancy.services.tenant import get_active_organisation_id, get_user_membership_organisations

        active_org = get_active_organisation_id(request) or user.organisation_id
        memberships = [
            str(x) for x in get_user_membership_organisations(user)
        ]
        data = {
            "role_code": role_code or "",
            "is_regulator": user.is_regulator,
            "is_superuser": user.is_superuser,
            "is_staff": user.is_staff,
            "organisation_id": active_org,
            "membership_organisation_ids": memberships,
            "permissions": _role_permissions(role_code),
        }
        return Response(PermissionsSerializer(data).data)
