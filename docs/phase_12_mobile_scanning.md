# Phase 12 — Mobile Operations + Real Device Scanning

Additive mobile scanning layer on top of Phase 8 verification, Phase 10 serialization/mobile APIs, and ecosystem portals.

## Frontend routes

| Route | Purpose |
|-------|---------|
| `/scan` | Scan operations hub |
| `/citizen/scan` | Citizen medicine verification |
| `/pharmacy/scan` | Pharmacy receive + dispense modes |
| `/regulator/field-inspection` | Regulator field checklist + scans |
| `/customs/scan` | Customs import verification |
| `/warehouse/scan` | Warehouse receiving |

## Backend APIs

| Method | Path | Auth |
|--------|------|------|
| POST | `/api/v1/scanning/ingest/` | Public for `citizen_verify`; JWT for operational roles |
| GET | `/api/v1/scanning/history/` | Authenticated |
| POST | `/api/v1/scanning/sync-pending/` | Authenticated batch offline sync |

### Ingest payload

```json
{
  "serial_number": "NG-NPTTE-…",
  "scan_type": "citizen_verify | pharmacy_receive | pharmacy_dispense | regulator_inspection | customs_verify | warehouse_receive",
  "actor_role": "citizen | pharmacy | regulator | customs | warehouse",
  "organisation": "<uuid optional>",
  "device_id": "nptte-device-…",
  "latitude": 6.45,
  "longitude": 3.39,
  "offline_timestamp": "2026-05-18T10:00:00Z",
  "sync_status": "pending | synced | failed",
  "replay_nonce": "…"
}
```

Existing Phase 10 mobile endpoints remain unchanged:

- `POST /api/v1/mobile/scans/ingest/`
- `POST /api/v1/mobile/scans/sync-offline/`

## Data model

**`ScanEvent`** (`apps.scanning`) — national scan ledger with serial, scan_type, user, organisation, geo, device_id, sync_status, risk_score, outcome_label, result_payload.

## Frontend modules

- `html5-qrcode` — browser camera QR/barcode (dynamic import, SSR-safe)
- `components/scanning/*` — camera, workflow, alerts, offline queue panel
- `store/offline-scan-queue-store.ts` — localStorage-backed queue with retry
- `services/scanning.ts` — API client

## Role outcomes

| Role | Example labels |
|------|----------------|
| Citizen | authentic, suspicious, recalled, expired |
| Pharmacy | received, dispensed, quarantined |
| Regulator | inspection_passed, flagged, seized |
| Customs | import_verified, held, suspicious |
| Warehouse | received, transferred, temperature_breach |

## Deployment (Render + Vercel)

1. **Render:** `python manage.py migrate` (applies `scanning.0001_initial`).
2. **Vercel:** redeploy frontend; ensure `NEXT_PUBLIC_API_BASE_URL` points to Render `/api/v1`.
3. **HTTPS required** for camera access on production devices.

## Risks

- Camera permissions denied on HTTP or blocked browsers — manual serial fallback always available.
- Duplicate `scanning` vs `mobile` ingest paths — clients should standardise on `/scanning/ingest/` for Phase 12 UIs.
- Offline queue stored in browser localStorage — not encrypted; operational devices should use managed profiles.
- Citizen ingest is public (rate-limited by existing verification throttling patterns) — monitor abuse.

## Verification commands

```bash
cd backend && python3 manage.py check
USE_SQLITE=1 python3 manage.py test tests.test_phase12_mobile_scanning

cd frontend && npm run build && npm test
```
