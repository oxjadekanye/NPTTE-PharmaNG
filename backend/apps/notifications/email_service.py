"""Phase 15 — provider-agnostic email delivery (console locally, pluggable in production)."""
from __future__ import annotations

import logging
from typing import Iterable

from django.conf import settings
from django.core.mail import send_mail

from apps.core.tasks import enqueue_task

logger = logging.getLogger("nptte.email")


def get_default_from_email() -> str:
    return getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@nptte.gov.ng")


def send_platform_email(
    *,
    subject: str,
    message: str,
    recipient_list: Iterable[str],
    html_message: str | None = None,
    async_delivery: bool = True,
) -> str:
    """
    Send email via Django EMAIL_BACKEND (console in dev).
    Uses enqueue_task when async_delivery=True for Celery-ready dispatch.
    """
    recipients = [r for r in recipient_list if r]
    if not recipients:
        return "skipped:no_recipients"

    def _send():
        send_mail(
            subject=subject,
            message=message,
            from_email=get_default_from_email(),
            recipient_list=recipients,
            html_message=html_message,
            fail_silently=False,
        )
        logger.info("Email sent to %s: %s", recipients, subject)

    if async_delivery:
        return enqueue_task("platform_email", _send)
    _send()
    return "sent:sync"
