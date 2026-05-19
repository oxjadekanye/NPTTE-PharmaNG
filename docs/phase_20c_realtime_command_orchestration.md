# Phase 20C — Realtime National Command Orchestration + Geospatial Intelligence

## Overview

Phase 20C extends NPTTE into a live sovereign command platform: geospatial layers, fullscreen command room, regional command centers, collaborative investigation rooms, patch-based realtime updates, scoped streambus channels, and expanded AI operational coordination (manual trigger only).

## Command room architecture

```
Operational data (orgs, scans, cases, alerts, tasks)
        ↓
command_orchestration services (geospatial, regional, command_room)
        ↓
REST snapshot APIs  +  streambus publish (patches)
        ↓
Frontend: CommandRoomWallboard + useRealtimePatches
```

- **Snapshot:** `GET /api/v1/command-orchestration/command-room/` — aggregated wallboard data (non-blocking refresh every 20s).
- **Patches:** SSE `type: patch` from `/api/v1/realtime/stream/?patches=1&channel=national` — incremental metric/entity/context updates without full dashboard rerenders.

## Geospatial intelligence

| Layer | API param | Data source |
|-------|-----------|-------------|
| National operational | `operational` | Organisations with lat/lng |
| Counterfeit hotspots | `counterfeit` | Suspicious `ScanEvent` |
| Recall impact | `recalls` | `NationalAlert` (recall) |
| Shortage pressure | `shortage` | `NationalAlert` (shortage) |
| Investigations | `investigations` | Open `EnforcementCase` |
| Enforcement deployment | `enforcement` | Escalated cases |
| Customs / border | `customs` | Customs scan events |

**Endpoint:** `GET /api/v1/command-orchestration/map-markers/?layer=&cluster=1`

Markers include organisation, severity, status, risk score, assigned officer, explorer shortcuts. Server-side grid clustering keeps payloads small.

### Frontend routes

| Route | Purpose |
|-------|---------|
| `/regulator/map` | National map hub |
| `/regulator/map/[layer]` | Layer-specific map |
| `/executive/map` | Ministerial geospatial view |
| `/command-room` | Fullscreen wallboard |

## Regional intelligence

Six zones: South West, South East, South South, North Central, North East, North West.

- `GET /api/v1/command-orchestration/regions/`
- `GET /api/v1/command-orchestration/regions/<region_key>/`

UI: `/regulator/regions`, `/regulator/regions/[regionKey]`

## Collaborative investigations

Models: `InvestigationNote`, `InvestigationComment` (enforcement app migration `0002`).

- `GET/POST /api/v1/command-orchestration/investigations/<case_id>/room/`
- Actions: `note`, `comment`, `transfer`
- Publishes `enforcement.investigation.*` events on `investigation` stream channel

UI: `/regulator/enforcement/cases/[caseId]/room`

## Streambus enhancements

- **Channels:** `national`, `regional`, `investigation`, `escalation`, `officer_tasks`, `executive` (payload `stream_channel`)
- **Redis:** `nptte:bus:channel:<name>` fan-out
- **Scoped replay:** `GET /api/v1/streambus/scoped-replay/?channel=investigation`
- **Patches:** embedded in event payload + SSE `type: patch`

## AI operational coordination

New copilot `prompt_mode` values (manual POST only):

- `operational_recommendations`
- `escalation_reasoning`
- `deployment_suggestions`
- `hotspot_prediction`
- `recall_spread_analysis`
- `shortage_forecast`

All require human review; deterministic fallback when OpenAI unavailable.

## Task orchestration

`GET /api/v1/command-orchestration/tasks/live/` — open tasks, overdue count, SLA indicator, regional queue hints.

## Performance strategy

- Map: lazy marker fetch, server clustering, Leaflet dynamic import (no SSR).
- Command room: shell renders immediately; data hydrates via parallel REST + SSE patches.
- Patches: Zustand `useRealtimePatchStore` — no full explorer bundle reload.
- Explorer/quick-bundle architecture unchanged.

## Deployment notes

### Render

1. `python manage.py migrate` (includes `enforcement.0002_investigation_collaboration`)
2. Ensure `REDIS_URL` for streambus channel fan-out and caches
3. Optional: `python manage.py seed_operational_demo_data` for map markers

### Vercel

Deploy frontend with existing `NEXT_PUBLIC_API_BASE_URL`. New routes are static/dynamic under `(regulator)`.

## Tests

```bash
cd backend && python manage.py check
USE_SQLITE=1 python manage.py test tests.test_phase20c_command_orchestration
cd frontend && npm run build && npm test
```

## Limitations

- Map clustering is grid-based (not true geospatial DB); PostGIS not enabled.
- SSE still polls DB every 5s; Redis channel subscribers not wired to SSE yet.
- Regional stats are aggregate heuristics, not live census.
- Command room AI ticker is placeholder text (briefing remains on-demand in executive/copilot panels).
- No WebSocket transport yet (`/realtime/transport/` remains metadata stub).
