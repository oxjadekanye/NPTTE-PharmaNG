# Phase 16 — External Connectivity & Integrations

## Overview

Phase 16 prepares NPTTE PharmaNG for real-world connectivity: pluggable email/SMS/push providers, cloud storage abstraction, PDF generation, webhooks, API key lifecycle, exports, analytics persistence, and an integration health dashboard.

## Provider architecture

### Email (`apps.integrations.providers.email`)

| Provider | Setting `NPTTE_EMAIL_PROVIDER` | Credentials |
|----------|-------------------------------|-------------|
| Console | `console` (default) | Django console backend |
| SMTP | `smtp` | `EMAIL_HOST`, `EMAIL_*` |
| SendGrid-ready | `sendgrid` | `SENDGRID_API_KEY` |
| Mailgun-ready | `mailgun` | `MAILGUN_API_KEY` |

Delivery logged in `EmailDeliveryLog` with retry-ready status fields.

### SMS (`apps.integrations.providers.sms`)

| Provider | Setting | Credentials |
|----------|---------|-------------|
| Mock | `mock` (default) | None |
| Twilio-ready | `twilio` | `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN` |
| Africa's Talking-ready | `africas_talking` | `AFRICAS_TALKING_API_KEY` |

Falls back to mock when credentials absent.

### Push (`apps.integrations.providers.push`)

- `PushDeviceRegistration` for web/mobile endpoints
- Mock dispatch (no production provider required)
- `POST /integrations/push/register/`

### Storage (`apps.integrations.storage.backends`)

| Backend | Setting | Env |
|---------|---------|-----|
| Local | `local` (default) | `MEDIA_ROOT` |
| S3-compatible | `s3` | `AWS_STORAGE_BUCKET_NAME` |
| GCS-ready | `gcs` | `GCS_BUCKET_NAME` |
| Azure-ready | `azure` | `AZURE_STORAGE_CONNECTION_STRING` |

Falls back to local when cloud credentials absent.

## Webhook system

- `WebhookSubscription` — URL, secret, event list, organisation scope
- `WebhookDeliveryLog` — retry count, HTTP status, payload
- `publish_integration_event()` — fan-out to subscribers

Events: `recall_created`, `batch_approved`, `suspicious_scan`, `onboarding_approved`, `organisation_suspended`

APIs:
- `GET/POST /integrations/webhooks/`
- `GET /integrations/webhooks/deliveries/`
- `POST /integrations/webhooks/test/`

## API key model

Extended `apps.developer_access`:
- `revoke_api_key()`, `rotate_api_key()`
- Usage logging updates `last_used_at`

Tenant-scoped keys via `POST /integrations/keys/` (org admins + regulators).

## PDF generation

`POST /integrations/pdf/generate/` — document types:
- `qr_label`, `batch_certificate`, `recall_notice`

Uses ReportLab when installed; minimal PDF fallback otherwise.

## Export/report engine

`ExportJob` model — CSV and PDF reports:
- `audit`, `recall`, `compliance`, `traceability`

`POST /integrations/exports/` — generate and store
`GET /integrations/exports/<id>/download/` — download

## Analytics persistence

`AnalyticsSnapshot` — scan counts, onboarding pending, activity, notifications, suspicious scans.

`GET/POST /integrations/analytics/`

## Health dashboard

`GET /integrations/health/` — email, SMS, storage, push, webhook status + queue metrics.

## External connectors

`ExternalIntegrationConnector` — pharmacy, ERP, warehouse, customs, manufacturer configs per organisation.

`GET/POST /integrations/connectors/`

## Deployment notes

1. Migrate: `python manage.py migrate` (`integrations.0001`)
2. Optional env (all additive):
   ```
   NPTTE_EMAIL_PROVIDER=smtp
   NPTTE_SMS_PROVIDER=mock
   NPTTE_STORAGE_BACKEND=local
   ```
3. Install PDF deps: `reportlab`, `qrcode` (in `requirements.txt`)
4. Webhook targets must accept POST JSON with `X-NPTTE-Event` and optional `X-NPTTE-Signature`

## Security

- Tenant isolation on keys, exports, connectors, webhooks
- Regulator-only: health dashboard, SMS send, delivery logs, webhook test
- API keys stored as SHA-256 hashes; raw key shown once on create/rotate
- Citizen verification and demo routes unchanged
