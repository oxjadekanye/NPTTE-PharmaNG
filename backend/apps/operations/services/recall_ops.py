"""Recall acknowledgement persistence and notifications."""
from apps.notifications.constants import NOTIFICATION_TYPE_RECALL, SEVERITY_CRITICAL, SEVERITY_SUCCESS
from apps.notifications.services.delivery import deliver_notification, notify_organisation_admins
from apps.operations.models import OperationalTask, WorkflowTimelineEntry
from apps.operations.services.tasks import create_operational_task
from apps.operations.services.workflow import record_workflow_event


def on_recall_acknowledged(*, campaign, organisation, actor, ack_type: str) -> None:
    record_workflow_event(
        workflow_type="recall",
        title=f"{ack_type.title()} recall acknowledged",
        summary=f"Campaign {campaign.campaign_code}",
        organisation=organisation,
        actor=actor,
        entity_type="recall_execution_campaign",
        entity_id=campaign.id,
        created_by=actor,
    )
    notify_organisation_admins(
        organisation=organisation,
        title="Recall acknowledgement recorded",
        body=f"Campaign {campaign.campaign_code} — {ack_type} acknowledgement logged.",
        severity=SEVERITY_SUCCESS,
        notification_type=NOTIFICATION_TYPE_RECALL,
        created_by=actor,
    )
    if campaign.pharmacies_targeted and campaign.pharmacies_acknowledged < campaign.pharmacies_targeted:
        unresolved = campaign.pharmacies_targeted - campaign.pharmacies_acknowledged
        if unresolved > 0 and actor:
            deliver_notification(
                recipient=actor,
                title="Unresolved recall acknowledgements",
                body=f"{unresolved} pharmacies still pending for {campaign.campaign_code}",
                severity=SEVERITY_CRITICAL,
                notification_type=NOTIFICATION_TYPE_RECALL,
                organisation=organisation,
                created_by=actor,
            )
            create_operational_task(
                title=f"Recall follow-up: {campaign.campaign_code}",
                task_type="recall_followup",
                organisation=organisation,
                description=f"{unresolved} pending acknowledgements",
                priority="high",
                related_entity_type="recall_execution_campaign",
                related_entity_id=campaign.id,
                created_by=actor,
            )
