from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.accounts.models import Role
from apps.core.api.responses import api_response
from apps.core.permissions import IsOrganisationMember, IsRegulatorUser
from apps.tenancy.models import OrganisationInvitation, OrganisationMembership
from apps.tenancy.permissions import HasTenantOrganisationAccess
from apps.tenancy.services.dashboard import organisation_dashboard
from apps.tenancy.services.invitations import accept_invitation, invite_user, resend_invitation, revoke_invitation
from apps.tenancy.services.onboarding import apply_organisation_onboarding, submit_onboarding_for_review
from apps.tenancy.services.regulator import (
    approve_onboarding_application,
    list_regulator_approval_queue,
    reactivate_organisation,
    reject_onboarding_application,
    suspend_organisation,
)
from apps.tenancy.services.tenant import (
    get_active_organisation_id,
    get_user_membership_organisations,
    log_tenant_access_denied,
    set_regulator_context,
    user_can_access_organisation,
)


class OnboardingApplyView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        data = request.data
        result = apply_organisation_onboarding(
            org_type_key=data.get("organisation_type", "manufacturer"),
            legal_name=data.get("legal_name", ""),
            trading_name=data.get("trading_name", ""),
            registration_number=data.get("registration_number", ""),
            license_number=data.get("license_number", ""),
            state=data.get("state", ""),
            city=data.get("city", ""),
            cac_number=data.get("cac_number", ""),
            contact_email=data.get("contact_email", ""),
            applicant_user=request.user if request.user.is_authenticated else None,
        )
        return api_response(data=result, message="Onboarding application created", status_code=201)


class OnboardingSubmitView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        onboarding = submit_onboarding_for_review(onboarding_id=pk)
        return api_response(data={"status": onboarding.status}, message="Submitted for regulator review")


class InvitationListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsOrganisationMember, HasTenantOrganisationAccess]

    def get(self, request):
        org_id = get_active_organisation_id(request)
        if not org_id:
            return api_response(data={"invitations": []}, message="No organisation context")
        invites = OrganisationInvitation.objects.filter(organisation_id=org_id).order_by("-created_at")[:50]
        rows = [
            {
                "id": str(i.id),
                "email": i.email,
                "status": i.invitation_status,
                "expires_at": i.expires_at.isoformat(),
                "role": i.role.code,
            }
            for i in invites
        ]
        return api_response(data={"invitations": rows}, message="Invitations")

    def post(self, request):
        org_id = get_active_organisation_id(request)
        email = request.data.get("email", "")
        role_code = request.data.get("role_code", "ORGANISATION_STAFF")
        role = Role.objects.filter(code=role_code).first()
        if not org_id or not role:
            return api_response(message="organisation and role_code required", status_code=400)
        from apps.organisations.models import Organisation

        inv = invite_user(
            organisation=Organisation.objects.get(pk=org_id),
            email=email,
            role=role,
            invited_by=request.user,
        )
        return api_response(
            data={"id": str(inv.id), "token": inv.token, "expires_at": inv.expires_at.isoformat()},
            message="Invitation sent",
            status_code=201,
        )


class InvitationResendView(APIView):
    permission_classes = [IsAuthenticated, IsOrganisationMember]

    def post(self, request, pk):
        inv = OrganisationInvitation.objects.get(pk=pk)
        if not user_can_access_organisation(request.user, inv.organisation_id):
            log_tenant_access_denied(request, organisation_id=inv.organisation_id)
            return api_response(message="Access denied", status_code=403)
        inv = resend_invitation(invitation=inv)
        return api_response(data={"token": inv.token}, message="Invitation resent")


class InvitationRevokeView(APIView):
    permission_classes = [IsAuthenticated, IsOrganisationMember]

    def post(self, request, pk):
        inv = OrganisationInvitation.objects.get(pk=pk)
        if not user_can_access_organisation(request.user, inv.organisation_id):
            return api_response(message="Access denied", status_code=403)
        revoke_invitation(invitation=inv)
        return api_response(message="Invitation revoked")


class InvitationAcceptView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        result = accept_invitation(token=request.data.get("token", ""), user=request.user)
        if not result.get("accepted"):
            return api_response(data=result, message="Invitation not accepted", status_code=400)
        return api_response(data=result, message="Invitation accepted")


class MembershipListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        org_id = get_active_organisation_id(request)
        qs = OrganisationMembership.objects.select_related("user", "role", "organisation")
        if org_id and not request.user.is_regulator:
            qs = qs.filter(organisation_id=org_id)
        elif org_id and request.user.is_regulator:
            qs = qs.filter(organisation_id=org_id)
        rows = [
            {
                "id": str(m.id),
                "user": m.user.username,
                "organisation_id": str(m.organisation_id),
                "role": m.role.code,
                "status": m.membership_status,
                "is_primary": m.is_primary,
            }
            for m in qs[:100]
        ]
        return api_response(data={"memberships": rows}, message="Memberships")


class TenantContextView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return api_response(
            data={
                "active_organisation_id": str(get_active_organisation_id(request) or ""),
                "membership_organisation_ids": [str(x) for x in get_user_membership_organisations(request.user)],
            },
            message="Tenant context",
        )


class TenantContextSwitchView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def post(self, request):
        org_id = request.data.get("organisation_id")
        if not org_id:
            return api_response(message="organisation_id required", status_code=400)
        switch = set_regulator_context(
            actor=request.user,
            organisation_id=org_id,
            reason=request.data.get("reason", "regulator_inspection"),
        )
        return api_response(
            data={"organisation_id": str(org_id), "switch_id": str(switch.id)},
            message="Organisation context switched",
        )


class OrganisationDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsOrganisationMember, HasTenantOrganisationAccess]

    def get(self, request):
        org_id = get_active_organisation_id(request)
        if not org_id:
            return api_response(message="No organisation context", status_code=400)
        return api_response(data=organisation_dashboard(organisation_id=org_id), message="Organisation dashboard")


class RegulatorApprovalQueueView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        rows = list_regulator_approval_queue(status=request.query_params.get("status"))
        return api_response(data={"queue": rows}, message="Approval queue")


class RegulatorApproveView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def post(self, request, pk):
        data = approve_onboarding_application(
            onboarding_id=pk, actor=request.user, notes=request.data.get("notes", "")
        )
        return api_response(data=data, message="Organisation approved")


class RegulatorRejectView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def post(self, request, pk):
        data = reject_onboarding_application(
            onboarding_id=pk, actor=request.user, reason=request.data.get("reason", "")
        )
        return api_response(data=data, message="Organisation rejected")


class RegulatorSuspendView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def post(self, request, org_id):
        org = suspend_organisation(
            organisation_id=org_id, actor=request.user, reason=request.data.get("reason", "")
        )
        return api_response(data={"organisation_id": str(org.id), "status": org.status}, message="Suspended")


class RegulatorReactivateView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def post(self, request, org_id):
        org = reactivate_organisation(organisation_id=org_id, actor=request.user)
        return api_response(data={"organisation_id": str(org.id), "status": org.status}, message="Reactivated")
