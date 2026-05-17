from django.db import models

from apps.core.constants import OnboardingStatus
from apps.core.models import NPTTEBaseModel
from apps.organisations.models import Organisation, OrganisationType


class OrganisationOnboarding(NPTTEBaseModel):
    organisation = models.OneToOneField(
        Organisation, on_delete=models.CASCADE, related_name="onboarding"
    )
    organisation_type = models.ForeignKey(OrganisationType, on_delete=models.PROTECT)
    status = models.CharField(
        max_length=32, choices=OnboardingStatus.CHOICES, default=OnboardingStatus.DRAFT, db_index=True
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]


class ComplianceSubmission(NPTTEBaseModel):
    onboarding = models.ForeignKey(
        OrganisationOnboarding, on_delete=models.CASCADE, related_name="compliance_submissions"
    )
    document_type = models.CharField(max_length=64, db_index=True)
    document_reference = models.CharField(max_length=255)
    submitted_at = models.DateTimeField(db_index=True)
    is_verified = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["-submitted_at"]


class LicenseVerification(NPTTEBaseModel):
    onboarding = models.ForeignKey(
        OrganisationOnboarding, on_delete=models.CASCADE, related_name="license_verifications"
    )
    license_number = models.CharField(max_length=128, db_index=True)
    issuing_authority = models.CharField(max_length=128, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    is_valid = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["-created_at"]


class ApprovalWorkflow(NPTTEBaseModel):
    onboarding = models.ForeignKey(
        OrganisationOnboarding, on_delete=models.CASCADE, related_name="approval_steps"
    )
    step_name = models.CharField(max_length=64, db_index=True)
    assigned_regulator_role = models.CharField(max_length=64, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_approved = models.BooleanField(null=True, blank=True)

    class Meta:
        ordering = ["created_at"]


class RegulatoryInspection(NPTTEBaseModel):
    onboarding = models.ForeignKey(
        OrganisationOnboarding, on_delete=models.CASCADE, related_name="inspections"
    )
    inspection_date = models.DateField(db_index=True)
    inspector_reference = models.CharField(max_length=128, blank=True)
    outcome = models.CharField(max_length=64, db_index=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-inspection_date"]
