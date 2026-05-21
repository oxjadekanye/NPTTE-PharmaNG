# Phase 11 — National Operational Hardening + Realtime Infrastructure

Additive layer on existing streambus, operations, intelligence, and mobile field apps. **No WebSocket rollout** — safe polling + event aggregation first.

## Realtime

| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/realtime/operational-feed/` | Aggregated poll feed (events, alerts, tasks, activity) |
| `GET /api/v1/realtime/prefetch/` | Route warm-up manifest |

Frontend: `services/realtime/`, `useRealtimeFeed`, `useOperationalSubscription`, TTL cache + in-process event bus.

## Field operations tasks

| Endpoint | Purpose |
|----------|---------|
| `GET/POST /api/v1/operations/tasks/` | List / create (existing) |
| `POST /api/v1/operations/tasks/create/` | Rich task create (assignee, evidence ref) |
| `GET /api/v1/operations/tasks/<id>/` | Detail + notes + evidence refs |
| `POST .../assign/`, `.../escalate/`, `.../notes/`, `.../evidence/` | Workflow |
| `GET /api/v1/operations/tasks/overdue/` | Overdue queue |
| `GET /api/v1/operations/tasks/calendar/` | Calendar horizon |
| `GET /api/v1/operations/field-operations/feed/` | Field feed |

Migration: `operations.0002_phase11_task_extensions` (notes, evidence_refs, completed_at).

## Executive intelligence

`GET /api/v1/intelligence/national-operations/` — shortage index, counterfeit heat, state compliance, readiness (demo-safe disclaimer).

Web: `/executive/national-ops`.

## Pharmacy inventory

`POST /api/v1/pharmacies/inventory/movement/` — stock movement  
`GET /api/v1/pharmacies/inventory/sync/` — reconciliation snapshot  

Web: `/pharmacy/inventory`.

## Citizen experience

| Endpoint | Purpose |
|----------|---------|
| `GET /public/verification-history/` | History + confidence |
| `GET /public/medication-search/` | Nearest pharmacy stock (demo) |
| `GET /public/safety-guidance/` | Deterministic safety copy |
| `GET /public/public-notices/` | Public notices |

Web: `/citizen/history`.

## Alerts

`GET /api/v1/alerts/center/` — grouped alert center with unread count.

Web: `/regulator/alert-center`. Mobile: `/alert-center`.

## Mobile field inspection

`GET /api/v1/mobile/evidence/timeline/` — chain-of-custody timeline  
`POST /api/v1/mobile/inspection/workflow/` — start / complete guided inspection  

Mobile: `/regulator/inspection-mode`.

## Performance

- Route prefetch via `useRoutePrefetch`
- Feed TTL cache (15s default)
- `OperationalSkeleton` loading UI
- Memoized `TaskPanel`

## Render / EAS

- Run `python manage.py migrate` on deploy
- No new env var names
- Expo: register `alert-center` in root Stack (done)
- Existing SSE stream unchanged

## Tests

`backend/tests/test_phase11_national_operational_hardening.py`
