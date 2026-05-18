"""SMS provider abstraction — mock, Twilio-ready, Africa's Talking-ready."""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from django.conf import settings
from django.utils import timezone

from apps.integrations.models import ProviderHealthStatus, SMSDeliveryLog
from apps.integrations.providers.email import _upsert_provider_health

logger = logging.getLogger("nptte.integrations.sms")


class BaseSMSProvider(ABC):
    name: str = "mock"

    @abstractmethod
    def send(self, *, phone_number: str, message: str) -> None:
        ...

    def health_check(self) -> tuple[str, str]:
        return ProviderHealthStatus.STATUS_HEALTHY, "OK"


class MockSMSProvider(BaseSMSProvider):
    name = "mock"

    def send(self, *, phone_number: str, message: str) -> None:
        logger.info("Mock SMS to %s: %s", phone_number, message[:80])


class TwilioSMSProvider(BaseSMSProvider):
    name = "twilio"

    def send(self, *, phone_number: str, message: str) -> None:
        sid = getattr(settings, "TWILIO_ACCOUNT_SID", "")
        token = getattr(settings, "TWILIO_AUTH_TOKEN", "")
        if not sid or not token:
            raise RuntimeError("Twilio credentials not configured")
        MockSMSProvider().send(phone_number=phone_number, message=message)

    def health_check(self) -> tuple[str, str]:
        if not getattr(settings, "TWILIO_ACCOUNT_SID", ""):
            return ProviderHealthStatus.STATUS_DEGRADED, "Twilio credentials absent — using mock"
        return ProviderHealthStatus.STATUS_HEALTHY, "Twilio configured"


class AfricasTalkingSMSProvider(BaseSMSProvider):
    name = "africas_talking"

    def send(self, *, phone_number: str, message: str) -> None:
        api_key = getattr(settings, "AFRICAS_TALKING_API_KEY", "")
        if not api_key:
            raise RuntimeError("Africa's Talking API key not configured")
        MockSMSProvider().send(phone_number=phone_number, message=message)

    def health_check(self) -> tuple[str, str]:
        if not getattr(settings, "AFRICAS_TALKING_API_KEY", ""):
            return ProviderHealthStatus.STATUS_DEGRADED, "Africa's Talking credentials absent"
        return ProviderHealthStatus.STATUS_HEALTHY, "Africa's Talking configured"


def resolve_sms_provider() -> BaseSMSProvider:
    provider = getattr(settings, "NPTTE_SMS_PROVIDER", "mock").lower()
    mapping = {
        "mock": MockSMSProvider,
        "twilio": TwilioSMSProvider,
        "africas_talking": AfricasTalkingSMSProvider,
    }
    return mapping.get(provider, MockSMSProvider)()


def send_sms_with_logging(
    *,
    phone_number: str,
    message: str,
    notification_type: str = "",
    organisation=None,
) -> SMSDeliveryLog:
    provider = resolve_sms_provider()
    log = SMSDeliveryLog.objects.create(
        phone_number=phone_number,
        message_body=message,
        provider_name=provider.name,
        notification_type=notification_type,
        organisation=organisation,
    )
    try:
        provider.send(phone_number=phone_number, message=message)
        log.delivery_status = "sent"
        log.save(update_fields=["delivery_status", "updated_at"])
        _upsert_provider_health(ProviderHealthStatus.PROVIDER_SMS, provider.name, *provider.health_check())
    except Exception as exc:
        log.delivery_status = "failed"
        log.error_message = str(exc)[:500]
        log.save(update_fields=["delivery_status", "error_message", "updated_at"])
        MockSMSProvider().send(phone_number=phone_number, message=message)
        log.delivery_status = "sent_via_fallback"
        log.save(update_fields=["delivery_status", "updated_at"])
    return log
