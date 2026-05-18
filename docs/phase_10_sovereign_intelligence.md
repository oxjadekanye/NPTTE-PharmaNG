# Phase 10 — Sovereign AI + Real Operational Intelligence

Additive operational layer. **No changes** to auth flows, RBAC contracts, Render/Vercel config, or existing stable API paths.

## New API prefixes (`/api/v1/`)

| Prefix | Endpoints |
|--------|-----------|
| `serialization/` | `dashboard/`, `decode/`, `labels/<uuid>/`, `packaging/`, `scan-history/` |
| `intelligence/` | `national/`, `serial-risk/` |
| `notifications/` | `center/`, `broadcast/` |
| `certificates/` | ``, `issue/`, `verify/` |
| `developer/` | `overview/`, `keys/` |
| `traceability/` | `custody/timeline/`, `custody/record/`, `recall-execution/`, `recall-execution/launch/` |
| `command-center/` | `incidents/assign/`, `incidents/escalate/` |
| `mobile/` | `scans/ingest/`, `scans/sync-offline/` |

Existing `verification/`, `public/verify/`, `traceability/transactions/`, SSE unchanged.

## Migrations (new only)

- `serialization/0004_phase10_serialization_operations.py` — GS1 fields, `SerialPackagingUnit`, `SerialScanRecord`
- `traceability/0004_phase10_custody_and_recall_execution.py` — custody ledger, recall execution
- `command_center/0002_phase10_incident_workflow.py` — incident workflow fields
- `mobile/0002_phase10_offline_scan_queue.py` — offline scan queue
- `certificates/0001_initial.py` — digital regulatory certificates
- `developer_access/0001_initial.py` — API keys and audit

## New frontend routes

| Route | Purpose |
|-------|---------|
| `/regulator/serialization` | Enterprise serialization dashboard |
| `/regulator/custody` | Live chain-of-custody timeline |
| `/command-center/notifications` | Notification center |
| `/developer` | Developer portal foundation |

## Render follow-up

```bash
python manage.py migrate
```

No new env vars required.

## Vercel

Redeploy frontend; `NEXT_PUBLIC_API_BASE_URL` unchanged.

## Testing

```bash
cd backend && python3 manage.py check
USE_SQLITE=1 python3 manage.py test tests
cd ../frontend && npm run build && npm test
```

## Seeded demo workflows

1. Regulator → `/regulator/serialization` — national serial KPIs.
2. `/regulator/custody` — lookup `NG-NPTTE-…` timeline.
3. Citizen verify — response includes `counterfeit_probability` when authentic.
4. `/developer` — API key overview (create via POST `/developer/keys/`).
5. POST `/certificates/verify/` with issued QR code.

## Performance

- Scan history capped at 100 rows per request.
- Offline sync processes 50 queued scans per call.
- Intelligence snapshot reuses existing `ai_engine` heuristics (no blocking ML).
