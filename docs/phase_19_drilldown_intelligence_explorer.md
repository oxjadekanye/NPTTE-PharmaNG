# Phase 19 — Drill-down intelligence explorer & clickable operational command

Additive operational intelligence layer: every major metric and feed item can open a **right-hand intelligence drawer** or a **full explorer detail page**, backed by tenant-safe `/api/v1/explorer/` APIs.

## Architecture

### Backend (`apps/explorer`)

| Concept | Implementation |
|---------|----------------|
| DrillDownRegistry | `services/registry.py` — supported `ENTITY_TYPES` |
| EntityResolutionService | `services/entity_resolution.py` — `resolve_entity()` |
| IntelligenceDetailService | `services/payloads.py` — `build_explorer_bundle()` |
| RelatedEntityService | `related_entities` slice of bundle (`nodes` / `edges` graph stub) |
| RiskBreakdownService | `services/risk_breakdown.py` — deterministic contributions |
| EvidenceTimelineService | `build_evidence_entries()` / `build_timeline_entries()` in `payloads.py` |
| OperationalActionService | `services/execute_action.py` — safe task / briefing / case actions |

### Tenant access (`services/access_control.py`)

- **Regulators**: national aggregates, all org-scoped records, enforcement without organisation (national scope).
- **Organisation users**: linked `organisation_id` on the underlying row; **regional_risk** only if the user’s organisation state matches; **command-activity-current** aggregate filtered to member organisations.
- **National aggregates** (`national-risk-current`, `open-alerts-current`, …): **regulator-only** except `command-activity-current`.
- **Notifications**: recipient match (non-regulator) or regulator.
- Denials logged via `TenantAccessLog` (`log_tenant_access_denied`).
- Regulator detail views optionally audited via `RegulatorOperationalHistory` (`action_type=explorer_detail`).

## Entity types

See `apps/explorer/constants.py` — includes `national_risk`, `regional_risk`, `product`, `scan_event`, `intelligence_signal`, `enforcement_case`, `notification`, `alert`, `task`, aggregates, etc.

## Aggregate pseudo-IDs

`national-risk-current`, `high-risk-current`, `open-alerts-current`, `fraud-flags-current`, `counterfeit-detections-current`, `active-investigations-current`, `products-tracked-current`, `recalls-current`, `command-activity-current`.

## API routes (`/api/v1/explorer/`)

| Method | Path |
|--------|------|
| GET | `resolve/?type=&id=` |
| GET | `detail/<entity_type>/<entity_id>/` |
| GET | `related/...` |
| GET | `timeline/...` |
| GET | `evidence/...` |
| GET | `actions/...` |
| GET | `risk-breakdown/...` |
| POST | `actions/<entity_type>/<entity_id>/execute/` |

Execute requires **regulator** JWT. Mutating actions honour `confirm: true` where required.

## Frontend routes

| Route | Purpose |
|-------|---------|
| `/regulator/explorer` | Hub links to common aggregates |
| `/regulator/explorer/[entityType]/[entityId]` | Full detail (filters, graph JSON, Phase 20 placeholder) |
| `/regulator/explorer/aggregate/[aggregateId]` | Redirects to canonical entity type + aggregate id |

**IntelligenceDetailDrawer** is mounted inside `CommandShell` for all national command pages using that shell.

### Clickable surfaces (non-exhaustive)

- National overview metric cards, national status banner, intelligence highlights, activity log, alert ticker.
- Command center overview metrics, live event feed telemetry & rows, intelligence feed.
- Executive GlassPanels and ministerial overview metrics / lists.
- Sovereign intelligence dashboard (national block, signals, regions, product table).
- Enforcement recommendations, cases (link + quick view), timeline (when `case_id` present).
- Notification center rows.

## Risk breakdown model

National breakdown exposes weighted contributions (suspicious scans, invalid serials, recalls, baseline), thresholds crossed, and Phase 18-aligned scores. Regional and product/org variants reuse Phase 18 scoring helpers.

## Action execution model

Non-destructive defaults: `create_task`, `record_acknowledgement`, `generate_briefing`, `open_investigation` (with confirm), `mark_false_positive` on recommendations. Creates operational tasks, activity feed entries, narratives, enforcement cases, streambus `explorer.action.executed` where applicable.

## Testing checklist

- `python3 manage.py check`
- `USE_SQLITE=1 python3 manage.py test tests`
- `npm run build` / `npm test`
- Manual: open drawer from overview → full page link; org user denied on national aggregate.

## Deployment

- **Render**: no new migrations. Deploy backend + run existing migrations only.
- **Vercel**: standard static deploy; new explorer routes included in build.

## Limitations

- Relationship graph is a **stub** (nodes/edges) until a graph engine is added.
- Many entity types return **minimal** payloads until wired to richer domain serializers.
- LLM / OpenAI **not** invoked (Phase 20 placeholder in UI).
- Aggregate `alert` + `open-alerts-current` uses `NationalAlert` listing; fraud aggregate may be sparse if no fraud-tagged alerts exist.

## Recommended next phase

- Graph visualization (force-directed or sovereign map layer).
- Deep links from streambus event payloads to explorer targets.
- Copilot panel with policy-grounded LLM summarisation of explorer bundle.
