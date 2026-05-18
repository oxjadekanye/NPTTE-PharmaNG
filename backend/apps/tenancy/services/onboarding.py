"""Phase 14 — organisation onboarding applications."""
from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.core.constants import OnboardingStatus, RecordStatus
from apps.onboarding.models import ComplianceSubmission, LicenseVerification, OrganisationOnboarding
from apps.organisations.models import Organisation, OrganisationType
from apps.tenancy.models import OrganisationMembership


ORG_TYPE_MAP = {
    "manufacturer": ("manufacturer", "Manufacturer"),
    "pharmacy": ("pharmacy", "Pharmacy"),
    "distributor": ("distributor", "Distributor"),
    "warehouse": ("logistics", "Logistics / Warehouse"),
    "hospital": ("hospital", "Hospital"),
    "customs": ("customs", "Customs"),
}

ROLE_FOR_ORG_TYPE = {
    "manufacturer": "MANUFACTURER",
    "pharmacy": "PHARMACY_ADMIN",
    "distributor": "DISTRIBUTOR",
    "warehouse": "WAREHOUSE_MANAGER",
    "hospital": "HOSPITAL_ADMIN",
    "customs": "CUSTOMS_ADMIN",
}


@transaction.atomic
def apply_organisation_onboarding(
    *,
    org_type_key: str,
    legal_name: str,
    trading_name: str = "",
    registration_number: str = "",
    license_number: str = "",
    state: str = "",
    city: str = "",
    cac_number: str = "",
    contact_email: str = "",
    applicant_user=None,
) -> dict:
    type_code, type_name = ORG_TYPE_MAP.get(org_type_key, ("other", "Other"))
    org_type, _ = OrganisationType.objects.get_or_create(code=type_code, defaults={"name": type_name})

    org = Organisation.objects.create(
        organisation_type=org_type,
        legal_name=legal_name,
        trading_name=trading_name or legal_name,
        registration_number=registration_number,
        license_number=license_number,
        state=state,
        city=city,
        email=contact_email,
        status=RecordStatus.DRAFT,
        is_active=False,
        metadata={"cac_number": cac_number, "onboarding_org_type": org_type_key},
        created_by=applicant_user,
    )

    onboarding = OrganisationOnboarding.objects.create(
        organisation=org,
        organisation_type=org_type,
        status=OnboardingStatus.DRAFT,
        created_by=applicant_user,
    )

    if license_number:
        LicenseVerification.objects.create(
            onboarding=onboarding,
            license_number=license_number,
            is_valid=False,
            created_by=applicant_user,
        )

    if cac_number:
        ComplianceSubmission.objects.create(
            onboarding=onboarding,
            document_type="cac_certificate",
            document_reference=cac_number,
            submitted_at=timezone.now(),
            is_verified=False,
            created_by=applicant_user,
        )

    return {
        "organisation_id": str(org.id),
        "onboarding_id": str(onboarding.id),
        "status": onboarding.status,
    }


@transaction.atomic
def submit_onboarding_for_review(*, onboarding_id) -> OrganisationOnboarding:
    onboarding = OrganisationOnboarding.objects.select_related("organisation").get(pk=onboarding_id)
    onboarding.status = OnboardingStatus.SUBMITTED
    onboarding.submitted_at = timezone.now()
    onboarding.save(update_fields=["status", "submitted_at", "updated_at"])
    return onboarding


def ensure_membership_for_user(*, user, organisation, role_code: str) -> OrganisationMembership:
    from apps.accounts.models import Role

    role, _ = Role.objects.get_or_create(code=role_code, defaults={"name": role_code.replace("_", " ")})
    membership, _ = OrganisationMembership.objects.get_or_create(
        user=user,
        organisation=organisation,
        defaults={
            "role": role,
            "membership_status": OrganisationMembership.STATUS_ACTIVE,
            "is_primary": True,
            "created_by": user,
        },
    )
    if not user.organisation_id:
        user.organisation = organisation
        user.role = role
        user.save(update_fields=["organisation", "role"])
    return membership
