# Phase 15 — Operational Persistence & Notification Infrastructure

## Overview

Phase 15 transforms NPTTE PharmaNG from a controlled operational prototype into a persistent platform with workflow continuity, notifications, document management, and operational task tracking — while preserving tenancy isolation, demo systems, and existing APIs.

## Notification architecture

### Models (`apps.notifications`)

Extended `Notification` with:

- `severity` — INFO, WARNING, CRITICAL, SUCCESS
- `notification_type` — onboarding, invitation, recall, approval, etc.
- `organisation` — tenant-scoped delivery
- `email_sent_at`, `email_status` — email delivery tracking

### Delivery

- **In-app:** `/api/v1/notifications/center/` (GET list, POST mark read)
- **Unread count:** `/api/v1/notifications/unread/`
- **Email:** `apps.notifications.email_service.send_platform_email()` — uses Django `EMAIL_BACKEND` (console locally)

### Hooks

Tenancy and recall events trigger notifications via `apps.operations.integrations`.

## Email configuration

Environment variables (additive, optional in production):

| Variable | Default |
|----------|---------|
| `EMAIL_BACKEND` | `django.core.mail.backends.console.EmailBackend` |
| `DEFAULT_FROM_EMAIL` | `noreply@nptte.gov.ng` |
| `NPTTE_FRONTEND_URL` | `http://localhost:3000` |

No provider is hardcoded. Swap `EMAIL_BACKEND` for SMTP or a transactional provider when ready.

## Workflow persistence (`apps.operations`)

| Model | Purpose |
|-------|---------|
| `WorkflowTimelineEntry` | Onboarding, invitations, recalls, approvals |
| `RegulatorOperationalHistory` | Immutable regulator actions |
| `OperationalDocument` | CAC, licences, inspection evidence (local `MEDIA_ROOT`) |
| `OperationalTask` | Assigned tasks with due dates and escalation |
| `ActivityFeedEntry` | Persistent organisation/regulator activity feeds |

### APIs (`/api/v1/operations/`)

- `workflow/timeline/` — tenant-scoped workflow history
- `regulator/history/` — regulator audit timeline
- `activity/feed/` — live activity feed
- `tasks/`, `tasks/<id>/complete/` — task engine
- `documents/` — upload and list (multipart)
- `organisation/settings/`, `organisation/profile/` — org profile & readiness

## Recall acknowledgements

- **Pharmacy:** `POST /api/v1/traceability/recall-execution/pharmacy-ack/`
- **Warehouse:** `POST /api/v1/traceability/recall-execution/warehouse-ack/` (new `WarehouseRecallAcknowledgement` model)

Acknowledgements record workflow events, notifications, and follow-up tasks when unresolved.

## Tenancy

All list endpoints use `filter_queryset_for_tenant` or organisation membership checks. Notifications filter by active organisation context for non-regulators.

## Frontend

- `NotificationCenter` — compact bell in enterprise portal header
- `OperationalBanners` — onboarding, tasks, readiness banners
- `TaskPanel` — open operational tasks
- Services: `operations.ts`, extended `notifications.ts`

## Deployment notes

1. Run migrations on Render:
   ```bash
   python manage.py migrate
   ```
   Applies: `notifications.0002`, `operations.0001`, `traceability.0006`

2. Optional production email:
   ```bash
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=...
   DEFAULT_FROM_EMAIL=noreply@your-domain.gov.ng
   NPTTE_FRONTEND_URL=https://your-vercel-app.vercel.app
   ```

3. Document uploads use `MEDIA_ROOT` until object storage is configured (`storage_key` field reserved for S3 migration).

## Security model

- Regulator history: regulator-only API
- Cross-tenant document/task access: denied via `user_can_access_organisation`
- Email invitation tokens: no secrets in logs; console backend in dev only
