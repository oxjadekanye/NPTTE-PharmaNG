# Phase 20A — Performance Optimization + True Entity Resolution

Additive layer on Phase 19 explorer. No removal of sovereign intelligence, enforcement, or streambus modules.

## Backend

### Redis / Django cache (`apps/explorer/services/cache.py`)

| Payload | TTL |
|---------|-----|
| National risk | 30s |
| Timeline | 20s |
| Enforcement | 60s |
| Narratives | 120s |

Wrapped via `cached_explorer()` on detail bundles, overview, timeline, evidence, risk breakdown, and related graph stubs.

### Invalidation (`apps/explorer/services/invalidate.py`)

Hooks on:

- Streambus publish (`on_streambus_event`)
- Enforcement action execute / case assign
- Recommendation accept/dismiss

### Context routing (`apps/explorer/services/context_router.py`)

`GET /api/v1/explorer/context-route/?context=<key>` maps dashboard keys (e.g. `counterfeit_detections`, `open_alerts`) to concrete entities (cluster, alert, case, scan) with aggregate fallback only when no rows exist.

### Split payloads

- `GET /api/v1/explorer/overview/<type>/<id>/` — light summary + record preview
- Timeline/evidence — paginated `page`, `page_size`

### Streambus enrichment

Events include `explorer_entity_type`, `explorer_entity_id`, `explorer_target` for live feed drill-down.

### Copilot placeholders (`apps/copilot/`)

Service boundaries only — no external LLM calls in 20A.

## Frontend

- `openExplorerFromContext()` / `openExplorerFromStreamEvent()` in `lib/explorer-routing.ts`
- `explorerContext` on metric cards → context-route before drawer open
- `IntelligenceDetailDrawer` — overview first, parallel section fetches, operational UI components (no raw JSON dumps)
- Executive briefing cached in `sessionStorage` (90s)
- `ensureAuthBootstrap()` deduplicates profile/permissions on login
- Dynamic import for `MinisterialOverview` on executive route

## Tests

`backend/tests/test_phase20a_performance.py`

## Phase 20B roadmap

1. Wire `apps/copilot` to policy-grounded LLM with tenant RBAC
2. Drawer copilot panel → live summaries from case/evidence context
3. Ministerial briefing generation with citation links to explorer entities
4. Investigative suggestion actions (non-destructive) with human confirm
