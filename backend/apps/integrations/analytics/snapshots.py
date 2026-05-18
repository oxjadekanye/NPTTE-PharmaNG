"""Persist operational analytics snapshots."""
from __future__ import annotations

from datetime import timedelta

from django.utils import timezone

from apps.integrations.models import AnalyticsSnapshot
from apps.notifications.models import Notification
from apps.onboarding.models import OrganisationOnboarding
from apps.operations.models import ActivityFeedEntry
from apps.scanning.models import ScanEvent


def persist_operational_analytics(*, organisation=None) -> AnalyticsSnapshot:
    now = timezone.now()
    period_start = now - timedelta(hours=24)
    metrics = {
        "scan_count": _count_scans(organisation, period_start),
        "verification_events": 0,
        "onboarding_pending": _count_onboarding_pending(organisation),
        "activity_events": _count_activity(organisation, period_start),
        "notifications_sent": _count_notifications(organisation, period_start),
        "suspicious_scan_alerts": _count_suspicious_scans(organisation, period_start),
    }
    return AnalyticsSnapshot.objects.create(
        metric_type="operational_daily",
        organisation=organisation,
        period_start=period_start,
        period_end=now,
        metrics=metrics,
    )


def _count_scans(organisation, since):
    qs = ScanEvent.objects.filter(created_at__gte=since)
    if organisation:
        qs = qs.filter(organisation=organisation)
    return qs.count()


def _count_onboarding_pending(organisation):
    qs = OrganisationOnboarding.objects.filter(status__in=["submitted", "under_review"])
    if organisation:
        qs = qs.filter(organisation=organisation)
    return qs.count()


def _count_activity(organisation, since):
    qs = ActivityFeedEntry.objects.filter(created_at__gte=since)
    if organisation:
        qs = qs.filter(organisation=organisation)
    return qs.count()


def _count_notifications(organisation, since):
    qs = Notification.objects.filter(created_at__gte=since)
    if organisation:
        qs = qs.filter(organisation=organisation)
    return qs.count()


def _count_suspicious_scans(organisation, since):
    qs = ScanEvent.objects.filter(created_at__gte=since).filter(outcome_label__icontains="suspicious")
    if organisation:
        qs = qs.filter(organisation=organisation)
    return qs.count()
