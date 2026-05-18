"""Phase 10 — recall propagation and pharmacy acknowledgement."""
from __future__ import annotations

import uuid

from django.db import transaction
from django.utils import timezone

from apps.traceability.models import PharmacyRecallAcknowledgement, RecallExecutionCampaign


@transaction.atomic
def launch_recall_campaign(*, batch_recall, pharmacies_targeted: int = 0, actor=None) -> RecallExecutionCampaign:
    code = f"REC-EXEC-{uuid.uuid4().hex[:10].upper()}"
    return RecallExecutionCampaign.objects.create(
        batch_recall=batch_recall,
        campaign_code=code,
        status="active",
        pharmacies_targeted=pharmacies_targeted,
        estimated_patient_exposure=pharmacies_targeted * 120,
        created_by=actor,
    )


@transaction.atomic
def acknowledge_pharmacy_recall(*, campaign, pharmacy_organisation, completion_pct: int = 100) -> PharmacyRecallAcknowledgement:
    ack, _ = PharmacyRecallAcknowledgement.objects.get_or_create(
        campaign=campaign,
        pharmacy_organisation=pharmacy_organisation,
        defaults={"completion_pct": completion_pct, "acknowledged_at": timezone.now()},
    )
    if not ack.acknowledged_at:
        ack.acknowledged_at = timezone.now()
        ack.completion_pct = completion_pct
        ack.save(update_fields=["acknowledged_at", "completion_pct", "updated_at"])
    campaign.pharmacies_acknowledged = campaign.pharmacy_acks.filter(acknowledged_at__isnull=False).count()
    campaign.save(update_fields=["pharmacies_acknowledged", "updated_at"])
    return ack
