"""Onboarding workflow templates per organisation type (Phase 11)."""
from __future__ import annotations

WORKFLOW_TEMPLATES = {
    "manufacturer": {
        "label": "Manufacturer",
        "required_documents": ["GMP certificate", "NAFDAC product dossier", "Manufacturing site plan"],
        "approval_steps": ["Document verification", "Site inspection", "Regulator sign-off"],
    },
    "distributor": {
        "label": "Distributor",
        "required_documents": ["Distribution licence", "Cold-chain SOP", "Insurance bond"],
        "approval_steps": ["Licence check", "Warehouse audit", "Corridor authorisation"],
    },
    "pharmacy": {
        "label": "Pharmacy",
        "required_documents": ["PCN licence", "Superintendent pharmacist ID", "Premises inspection"],
        "approval_steps": ["PCN validation", "NAFDAC linkage", "Activation"],
    },
    "warehouse": {
        "label": "Warehouse",
        "required_documents": ["Bonded warehouse licence", "Temperature monitoring plan"],
        "approval_steps": ["Facility inspection", "Integration test", "Go-live"],
    },
    "hospital_pharmacy": {
        "label": "Hospital pharmacy",
        "required_documents": ["Hospital licence", "Formulary committee approval"],
        "approval_steps": ["Clinical governance review", "Activation"],
    },
    "regulator_user": {
        "label": "Regulator user",
        "required_documents": ["Government ID", "Agency appointment letter"],
        "approval_steps": ["Security clearance", "RBAC role assignment"],
    },
}


def onboarding_workflow_board() -> list[dict]:
    from apps.core.constants import OnboardingStatus
    from apps.onboarding.models import OrganisationOnboarding

    board = []
    for key, template in WORKFLOW_TEMPLATES.items():
        qs = OrganisationOnboarding.objects.filter(
            organisation_type__code__icontains=key.split("_")[0]
        ).select_related("organisation")[:5]
        entries = [
            {
                "organisation": o.organisation.legal_name,
                "status": o.status,
                "compliance_status": "verified" if o.status == OnboardingStatus.APPROVED else "pending",
                "assigned_reviewer": o.metadata.get("assigned_reviewer", "Unassigned"),
                "next_action": _next_action(o.status),
                "audit_history": o.metadata.get("audit_history", []),
            }
            for o in qs
        ]
        if not entries:
            entries = [
                {
                    "organisation": f"(DEMO) Pending {template['label']} applicant",
                    "status": OnboardingStatus.UNDER_REVIEW,
                    "compliance_status": "pending",
                    "assigned_reviewer": "NAFDAC Desk",
                    "next_action": "Submit required documents",
                    "audit_history": [{"at": "demo", "event": "SIMULATED onboarding placeholder"}],
                    "is_demo": True,
                }
            ]
        board.append(
            {
                "workflow_type": key,
                "label": template["label"],
                "required_documents": template["required_documents"],
                "approval_steps": template["approval_steps"],
                "entries": entries,
            }
        )
    return board


def _next_action(status: str) -> str:
    mapping = {
        "draft": "Complete application",
        "under_review": "Await regulator review",
        "approved": "Activate operations",
        "rejected": "Address rejection and resubmit",
    }
    return mapping.get(status, "Contact NPTTE support")
