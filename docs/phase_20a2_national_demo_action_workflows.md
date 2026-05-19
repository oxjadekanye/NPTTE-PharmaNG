# Phase 20A.2 — National Demo Data + Action Workflows

## Seed command

```bash
cd backend
python3 manage.py seed_operational_demo_data          # full national scale
python3 manage.py seed_operational_demo_data --lite   # CI / quick local
python3 manage.py seed_operational_demo_data --force  # additive re-run
```

All records tagged `metadata.demo_type = national_operational_demo`.

## Scale (full)

- 40 pharmacies, 15 manufacturers, 20 distributors, 12 warehouses, 8 customs, 12 hospitals, 6 regulator units, 6 enforcement teams
- 60+ products, 180+ batches, 3000 serials, 2000 scan events
- 600+ alerts/signals across 18 operational categories
- 30 assignable demo staff (`demo_staff_*` users)

## Explorer contexts

Dashboard cards resolve via `GET /api/v1/explorer/context-route/` then load rich bundles from `GET /api/v1/explorer/context-bundle/?context=`.

Executive contexts include: `live_national_threat_composite`, `api_health`, `national_ai_intelligence`, `medicine_stability`, `counterfeit_risk_forecast`, `shortage_pressure`, `import_disruption`, `enforcement_readiness`, `urgent_actions`, etc.

Command contexts include: `counterfeit_detections`, `invalid_serials`, `open_alerts`, `customs_holds`, `cold_chain_breaches`, etc.

Full context page: `/regulator/explorer/context/[contextKey]`

## Action workflows

| Action | Workflow |
|--------|----------|
| Create operational task | Modal with assignee, due date/time, priority |
| Acknowledge reviewed | Confirm + audit + alert metadata |
| Generate intelligence briefing | OpenAI if `OPENAI_API_KEY`, else deterministic |
| Open investigation | Case + optional investigator assign |
| Escalate alert | Alert escalation record + streambus |

Staff list: `GET /api/v1/explorer/staff/`

## AI

Server-side only in `apps/copilot/services/briefing.py`. Never exposes API keys. User-triggered via **Generate intelligence briefing** only.

## Performance

- Context bundles cached (Redis/Django) with national TTL
- Paginated records on detail and context pages
- Parallel drawer fetches (overview + sections)
- Executive briefing sessionStorage cache (90s) from Phase 20A

## Deploy

- **Render:** run `python manage.py seed_operational_demo_data` once on staging/demo; no new migrations
- **Vercel:** frontend only; ensure `NEXT_PUBLIC_API_URL` points to seeded backend

## Tests

`backend/tests/test_phase20a2_national_demo.py`

## Limitations

- Seed is additive with `--force`; not a full wipe
- OpenAI requires `OPENAI_API_KEY` on Render
- Map placeholders not yet geographic tiles
- Some legacy cards may still deep-link to entity pages

## Phase 20B

Wire copilot panel, policy grounding corpus, and ministerial narrative generation on top of context bundles.
