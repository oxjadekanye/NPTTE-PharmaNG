# Phase 13 — Realistic National Demo Data + End-to-End Traceability Walkthrough

Additive demo layer for live presentations. Does not alter auth, RBAC, CORS, or existing APIs.

## Management commands

```bash
# Seed full ecosystem journey (idempotent)
python manage.py seed_traceability_demo

# Optional re-run after manual clear
python manage.py seed_traceability_demo --force

# Remove ONLY tagged demo data
python manage.py clear_traceability_demo
```

All seeded rows include `metadata.demo_type = "traceability_demo"`.

## Demo serials (citizen testing)

| Scenario | Serial |
|----------|--------|
| Authentic | `NG-NPTTE-TD-PARACETAMOL-2026-AUTH000001` |
| Recalled | `NG-NPTTE-TD-AMOXICILLIN-2026-RECALL000001` |
| Suspicious | `NG-NPTTE-TD-METFORMIN-2026-SUSPIC000001` |
| Expired | `NG-NPTTE-TD-PARACETAMOL-2025-EXP0000001` |
| Invalid | `NG-NPTTE-TD-INVALID-000000001` (not in registry) |

## API

`GET /api/v1/demo/traceability-story/` — public story payload for UI (no auth).

## Frontend routes

| Route | Audience |
|-------|----------|
| `/regulator/live-demo` | Regulator walkthrough (timeline, custody, recall, audit) |
| `/citizen/demo-verify` | Public demo serial cards + live verify |

## Seed contents

- 2 manufacturers, 3 products, 4 batches (hero, recall, expired, suspicious)
- Distributor, warehouse, pharmacy nodes
- Supply-chain transactions + custody events
- Pharmacy receipt/dispense scan records
- Citizen verification logs
- One national recall + campaign metadata

## Deployment

1. **Render:** deploy backend; run `python manage.py seed_traceability_demo` once on staging/production demo environment.
2. **Vercel:** redeploy frontend; no new env vars.
3. **Cleanup:** `clear_traceability_demo` before re-seeding on shared DBs.

## Safety

- Cleanup deletes only `metadata.demo_type = traceability_demo` (and verification logs for demo serial numbers).
- Production records without the tag are never removed.
- Separate from Phase 11 `pilot_demo` tag.
