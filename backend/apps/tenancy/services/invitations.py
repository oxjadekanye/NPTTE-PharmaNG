"""Phase 14 — organisation user invitations."""
from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.tenancy.models import OrganisationInvitation, OrganisationMembership
from apps.tenancy.services.onboarding import ensure_membership_for_user

User = get_user_model()


@transaction.atomic
def invite_user(*, organisation, email: str, role, invited_by, days_valid: int = 7) -> OrganisationInvitation:
    OrganisationInvitation.objects.filter(
        organisation=organisation,
        email__iexact=email,
        invitation_status=OrganisationInvitation.STATUS_PENDING,
    ).update(invitation_status=OrganisationInvitation.STATUS_REVOKED)

    invitation = OrganisationInvitation.objects.create(
        organisation=organisation,
        email=email.lower().strip(),
        role=role,
        token=OrganisationInvitation.generate_token(),
        expires_at=timezone.now() + timedelta(days=days_valid),
        invited_by=invited_by,
        created_by=invited_by,
    )
    from apps.operations.integrations import on_invitation_created

    on_invitation_created(invitation=invitation, invited_by=invited_by)
    return invitation


def resend_invitation(*, invitation: OrganisationInvitation) -> OrganisationInvitation:
    invitation.token = OrganisationInvitation.generate_token()
    invitation.expires_at = timezone.now() + timedelta(days=7)
    invitation.invitation_status = OrganisationInvitation.STATUS_PENDING
    invitation.save(update_fields=["token", "expires_at", "invitation_status", "updated_at"])
    return invitation


def revoke_invitation(*, invitation: OrganisationInvitation) -> OrganisationInvitation:
    invitation.invitation_status = OrganisationInvitation.STATUS_REVOKED
    invitation.save(update_fields=["invitation_status", "updated_at"])
    return invitation


@transaction.atomic
def accept_invitation(*, token: str, user=None) -> dict:
    invitation = OrganisationInvitation.objects.select_related("organisation", "role").get(
        token=token, invitation_status=OrganisationInvitation.STATUS_PENDING
    )
    if invitation.is_expired():
        invitation.invitation_status = OrganisationInvitation.STATUS_EXPIRED
        invitation.save(update_fields=["invitation_status", "updated_at"])
        return {"accepted": False, "reason": "expired"}

    if user is None:
        user = User.objects.filter(email__iexact=invitation.email).first()
    if user is None:
        return {"accepted": False, "reason": "user_required", "email": invitation.email}

    membership, _ = OrganisationMembership.objects.update_or_create(
        user=user,
        organisation=invitation.organisation,
        defaults={
            "role": invitation.role,
            "membership_status": OrganisationMembership.STATUS_ACTIVE,
            "is_primary": not user.organisation_id,
            "invited_by": invitation.invited_by,
            "created_by": invitation.invited_by,
        },
    )
    if not user.organisation_id:
        user.organisation = invitation.organisation
        user.role = invitation.role
        user.save(update_fields=["organisation", "role"])

    invitation.invitation_status = OrganisationInvitation.STATUS_ACCEPTED
    invitation.accepted_by = user
    invitation.accepted_at = timezone.now()
    invitation.save(update_fields=["invitation_status", "accepted_by", "accepted_at", "updated_at"])

    from apps.operations.integrations import on_invitation_accepted

    on_invitation_accepted(invitation=invitation, user=user)

    return {
        "accepted": True,
        "organisation_id": str(invitation.organisation_id),
        "membership_id": str(membership.id),
    }
