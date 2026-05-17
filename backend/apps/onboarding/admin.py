from django.contrib import admin

from apps.onboarding.models import (
    ApprovalWorkflow,
    ComplianceSubmission,
    LicenseVerification,
    OrganisationOnboarding,
    RegulatoryInspection,
)

admin.site.register(OrganisationOnboarding)
admin.site.register(ComplianceSubmission)
admin.site.register(LicenseVerification)
admin.site.register(ApprovalWorkflow)
admin.site.register(RegulatoryInspection)
