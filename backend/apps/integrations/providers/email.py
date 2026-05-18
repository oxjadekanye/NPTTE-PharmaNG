"""Email provider abstraction — console, SMTP, SendGrid-ready, Mailgun-ready."""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Iterable

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from apps.integrations.models import EmailDeliveryLog, ProviderHealthStatus

logger = logging.getLogger("nptte.integrations.email")


class BaseEmailProvider(ABC):
    name: str = "base"

    @abstractmethod
    def send(self, *, subject: str, message: str, recipient_list: Iterable[str], html_message: str | None = None) -> None:
        ...

    def health_check(self) -> tuple[str, str]:
        return ProviderHealthStatus.STATUS_HEALTHY, "OK"


class ConsoleEmailProvider(BaseEmailProvider):
    name = "console"

    def send(self, *, subject: str, message: str, recipient_list: Iterable[str], html_message: str | None = None) -> None:
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@nptte.gov.ng"),
            recipient_list=list(recipient_list),
            html_message=html_message,
            fail_silently=False,
        )


class SMTPEmailProvider(BaseEmailProvider):
    name = "smtp"

    def send(self, *, subject: str, message: str, recipient_list: Iterable[str], html_message: str | None = None) -> None:
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@nptte.gov.ng"),
            recipient_list=list(recipient_list),
            html_message=html_message,
            fail_silently=False,
        )

    def health_check(self) -> tuple[str, str]:
        host = getattr(settings, "EMAIL_HOST", "")
        if not host:
            return ProviderHealthStatus.STATUS_UNAVAILABLE, "EMAIL_HOST not configured"
        return ProviderHealthStatus.STATUS_HEALTHY, f"SMTP host {host}"


class SendGridEmailProvider(BaseEmailProvider):
    """SendGrid-ready — uses SMTP relay when SENDGRID_API_KEY maps to EMAIL_HOST."""

    name = "sendgrid"

    def send(self, *, subject: str, message: str, recipient_list: Iterable[str], html_message: str | None = None) -> None:
        api_key = getattr(settings, "SENDGRID_API_KEY", "")
        if not api_key:
            raise RuntimeError("SENDGRID_API_KEY not configured")
        SMTPEmailProvider().send(
            subject=subject, message=message, recipient_list=recipient_list, html_message=html_message
        )

    def health_check(self) -> tuple[str, str]:
        if not getattr(settings, "SENDGRID_API_KEY", ""):
            return ProviderHealthStatus.STATUS_DEGRADED, "SendGrid credentials absent — fallback available"
        return ProviderHealthStatus.STATUS_HEALTHY, "SendGrid configured"


class MailgunEmailProvider(BaseEmailProvider):
    """Mailgun-ready — uses Django email when MAILGUN_API_KEY present."""

    name = "mailgun"

    def send(self, *, subject: str, message: str, recipient_list: Iterable[str], html_message: str | None = None) -> None:
        if not getattr(settings, "MAILGUN_API_KEY", ""):
            raise RuntimeError("MAILGUN_API_KEY not configured")
        SMTPEmailProvider().send(
            subject=subject, message=message, recipient_list=recipient_list, html_message=html_message
        )

    def health_check(self) -> tuple[str, str]:
        if not getattr(settings, "MAILGUN_API_KEY", ""):
            return ProviderHealthStatus.STATUS_DEGRADED, "Mailgun credentials absent"
        return ProviderHealthStatus.STATUS_HEALTHY, "Mailgun configured"


def resolve_email_provider() -> BaseEmailProvider:
    provider = getattr(settings, "NPTTE_EMAIL_PROVIDER", "console").lower()
    mapping = {
        "console": ConsoleEmailProvider,
        "smtp": SMTPEmailProvider,
        "sendgrid": SendGridEmailProvider,
        "mailgun": MailgunEmailProvider,
    }
    cls = mapping.get(provider, ConsoleEmailProvider)
    return cls()


def send_email_with_logging(
    *,
    subject: str,
    message: str,
    recipient_list: Iterable[str],
    html_message: str | None = None,
    organisation=None,
    max_retries: int = 3,
) -> EmailDeliveryLog:
    provider = resolve_email_provider()
    recipients = [r for r in recipient_list if r]
    log = EmailDeliveryLog.objects.create(
        recipient=",".join(recipients) or "none",
        subject=subject,
        provider_name=provider.name,
        delivery_status="pending",
        organisation=organisation,
    )
    try:
        provider.send(subject=subject, message=message, recipient_list=recipients, html_message=html_message)
        log.delivery_status = "sent"
        log.save(update_fields=["delivery_status", "updated_at"])
        _upsert_provider_health(ProviderHealthStatus.PROVIDER_EMAIL, provider.name, *provider.health_check())
    except Exception as exc:
        log.retry_count += 1
        log.error_message = str(exc)[:500]
        log.delivery_status = "failed" if log.retry_count >= max_retries else "retry"
        log.save(update_fields=["delivery_status", "retry_count", "error_message", "updated_at"])
        _upsert_provider_health(
            ProviderHealthStatus.PROVIDER_EMAIL,
            provider.name,
            ProviderHealthStatus.STATUS_DEGRADED,
            str(exc)[:200],
        )
        if log.delivery_status == "retry":
            raise
    return log


def _upsert_provider_health(provider_type: str, provider_name: str, status: str, message: str) -> None:
    ProviderHealthStatus.objects.update_or_create(
        provider_type=provider_type,
        provider_name=provider_name,
        defaults={"status": status, "message": message, "last_checked_at": timezone.now()},
    )
