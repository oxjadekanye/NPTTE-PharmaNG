# Phase 9 — National Pharmaceutical Operating Ecosystem

Additive national operating layer on top of existing regulator command, traceability, serialization, verification, SSE, and Render/Vercel deployments. **No breaking changes** to auth, RBAC contracts, stable API paths, or applied migrations.

## New frontend routes

| Path | Description |
|------|-------------|
| `/manufacturer` | Manufacturer operations portal (KPIs, intelligence bus, AI risk strip, modules) |
| `/pharmacy` | Pharmacy operations portal |
| `/warehouse` | Warehouse & logistics portal |
| `/customs` | Customs intelligence portal |
| `/distributor` | Distributor portal |
| `/hospital` | Hospital pharmacy portal |
| `/ert` | Emergency response teams portal |
| `/executive` | Executive / ministerial mode (dynamic-loaded overview + API snapshot) |
| `/command-center/recalls` | National recall operations center |
| `/citizen` | **Enhanced** mobile-first citizen verification (outcome mapping, reporting) |

Existing routes (e.g. `/regulator`, `/command-center`, `/command-center/threat-map`, `/command-center/incidents`, `/emergency-ops`) are unchanged.

## New backend APIs

| Method | Path | Auth | Notes |
|--------|------|------|-------|
| `GET` | `/api/v1/events/national-summary/` | JWT + regulator | Aggregate snapshot + tail of `EventStreamService` events for dashboards |

Existing endpoints are untouched.

## Migrations

**None** for Phase 9 (frontend-heavy + one read-only DRF view).

## New services & libraries

### Backend

- `NationalOperationsSummaryView` in `apps/events/api/views.py`
- URL: `apps/events/api/urls.py` → `national-summary/`

### Frontend

- `src/store/intelligence-bus-store.ts` — central intelligence bus simulation (Zustand).
- `src/intelligence/ai-risk-simulation.ts` — deterministic client-side “AI” risk scores.
- `src/services/national-operations.ts` — typed client for national summary.
- `src/components/portals/EnterprisePortalShell.tsx` — enterprise portal chrome.
- `src/components/portals/OperationalPortalTemplate.tsx` — shared portal dashboard template.
- `src/components/enterprise/GlassPanel.tsx`, `RiskScoreStrip.tsx`.
- `src/config/portal-nav.ts` — ecosystem hub navigation.
- `src/components/incidents/IncidentWorkflowPanel.tsx` — assignment, escalation, custody, enforcement UI.
- Demo map data: `WAREHOUSE_HUBS`, `CUSTOMS_MARKERS`, `INVESTIGATION_ZONES` in `src/demo/nigeria-intelligence.ts`.
- `useSimulatedRealtime` now also pushes to the intelligence bus (additive).

## Deployment notes

### Render (backend)

- No new environment variables required for the summary endpoint.
- Deploy as usual; run `python manage.py migrate` only when future phases add migrations.

### Vercel (frontend)

- Ensure `NEXT_PUBLIC_API_BASE_URL` points at the Render API host so `/executive` can load `GET /events/national-summary/` with a regulator JWT.
- Citizen and public routes remain static-friendly.

## Testing summary

- **Backend:** `python manage.py check` and `USE_SQLITE=1 python manage.py test tests` — includes `test_phase9_national_operations.py` (auth + regulator happy path + anonymous 401).
- **Frontend:** `npm run build`, `npm test` (Vitest).

## Seeded demo workflows

1. Log in as regulator → open `/executive` to see ministerial KPIs + optional live API snapshot.
2. Open any ecosystem portal (`/manufacturer`, `/pharmacy`, …) — shared nav, intelligence bus ticks, AI risk strip.
3. `/command-center/recalls` — acknowledgement progress simulation + embedded sovereign map.
4. `/command-center/threat-map` — layer toggles (state risk, pharmacy density, shortage, customs, investigations, logistics).
5. `/citizen` — verify serial; observe mapped outcomes; submit counterfeit / pharmacy complaint (uses public API where applicable).

## Performance considerations

- `MinisterialOverview` and `NigeriaThreatMap` on recall page are **lazy-loaded** (`next/dynamic`, `ssr: false`) to reduce initial JS on those routes.
- Intelligence bus caps events at 200; command feed remains capped as before.
- Map layer toggles memoise derived points to limit Leaflet churn.

## RBAC note

Ecosystem portals currently use `RegulatorGuard` with default `regulatory.read` so existing regulator operators can review the full national prototype. **Splitting** to manufacturer/pharmacy-specific roles would be a follow-up: clone `RegulatorGuard` + map `permission` strings to backend `_role_permissions` without renaming existing permissions.
