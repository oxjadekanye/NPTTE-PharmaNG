# Phase 17 — Realtime Event Streaming & Distributed Operational Intelligence

## Overview

Phase 17 adds an enterprise operational event bus, Redis-ready pub/sub with in-memory fallback, tenant-scoped live feeds, telemetry aggregation, alert escalation, and SSE-based realtime dashboards.

## Event architecture

### Operational Event Bus (`apps.streambus`)

`publish_operational_event()` wraps `EventStreamService.publish_event()` and adds:

- **Correlation IDs** — UUID per event chain
- **Lifecycle audit** — `EventLifecycleLog` (published, delivered, replayed, acknowledged)
- **Pub/sub fan-out** — `nptte:bus:{organisation_id}` and `nptte:bus:national`
- **Deferred processing** — `DeferredProcessingTask` queue (inline when Celery absent)
- **Escalation** — suspicious scans, recalls, warnings → notifications + webhooks

### Typed events

| Event | Constant |
|-------|----------|
| Scan completed | `scan.completed` |
| Suspicious scan | `scan.suspicious` |
| Onboarding | `onboarding.updated` |
| Recall | `recall.propagated` |
| Approval | `approval.recorded` |
| Telemetry tick | `telemetry.tick` |

Scan ingestion auto-publishes to the bus (non-blocking).

## Redis abstraction

`apps.core.redis_bus`:

- `RedisPubSub` when `REDIS_URL` is set
- `InMemoryPubSub` fallback locally (no Redis required)
- Used by `EventStreamService._broadcast` and streambus publish

## WebSocket / SSE model

| Transport | Endpoint | Status |
|-----------|----------|--------|
| SSE | `GET /api/v1/realtime/stream/` | Active |
| WebSocket metadata | `GET /api/v1/realtime/transport/` | Channels-ready stub |

SSE supports JWT via `?token=` query param and tenant `organisation_id` filtering.

## APIs (`/api/v1/streambus/`)

| Route | Purpose |
|-------|---------|
| `publish/` | Publish operational event |
| `replay/` | Tenant-scoped event replay |
| `acknowledge/<event_id>/` | Acknowledge event |
| `telemetry/` | Telemetry snapshots |
| `escalations/` | Live escalations |
| `lifecycle/` | Event audit trail (regulator) |
| `deferred-queue/` | Pending async tasks |
| `command-center/live/` | Live dashboard bundle |

## Telemetry

`OperationalTelemetrySnapshot` aggregates per window:

- Scan throughput
- Event throughput
- Verification / suspicious rates
- Onboarding velocity
- Recall execution %

## Tenant isolation

- Organisation users: replay and SSE filtered to their org
- Regulators: national visibility
- Cross-tenant replay denied via org context

## Deployment recommendations

1. **Migrate:** `python manage.py migrate` (`streambus.0001`)
2. **Redis (optional):** set `REDIS_URL` on Render for pub/sub scale
3. **SSE:** ensure proxy disables buffering (`X-Accel-Buffering: no` already set)
4. **Channels (future):** replace SSE generator with Channels consumer; keep event envelope unchanged

## Scaling notes

- Event batching: SSE polls every 5s, max 20 events per tick
- Telemetry in SSE: every 30s to limit DB load
- Lifecycle logs: index on `organisation`, `correlation_id`
- Deferred tasks: Celery-ready via `enqueue_task`
