# Phase 8 — National pharmaceutical traceability engine

This document describes the **additive** Phase 8 work that turns NPTTE PharmaNG toward a full national medicine traceability platform while **preserving** existing apps, URLs, auth, RBAC, CORS, and deployment behaviour.

## Summary

- **Batch lifecycle** (`lifecycle_status` on `ProductBatch`): `draft`, `approved`, `active`, `suspended`, `recalled`, `expired`, `destroyed` — parallel to existing `regulator_status` (`pending`, `approved`, `suspended`, `rejected`).
- **Serial format**: `NG-NPTTE-{PRODUCTCODE}-{YEAR}-{SEQUENCE}` — product code prefers `national_product_code`, else legacy name slug.
- **Serial custody** (`ProductSerial`): optional `custody_organisation` for pharmacy receipt / dispense rules.
- **Regulatory audit** (`BatchRegulatoryAudit`): immutable per-batch action trail (approve, reject, suspend, recall, serials issued, etc.).
- **Verification** (`POST /api/v1/verification/authenticate/`): enriched payload (`result`, `duplicate_scan_warning`, `safety_message`, `next_action`, `manufacturer`, `lifecycle_status`, optional `device_id`); batch state refreshed from DB before policy checks.
- **Manufacturer workflow**: register product, create batch (serials **not** issued on create), submit for approval, generate serials **only** after regulator approval.
- **Pharmacy workflow**: receive batch serials into custody + inventory; dispense serial with custody check.
- **Recall enforcement**: national recall record + lifecycle; verification returns `recalled`; `GET` affected pharmacy org IDs.

All operational demo data remains clearly labelled where applicable in the UI; engine data is **real ORM-backed** when APIs are used.

## Routes added or extended

| Method | Path | Notes |
|--------|------|--------|
| POST | `/api/v1/manufacturers/products/register/` | Register product (manufacturer staff) |
| POST | `/api/v1/manufacturers/batches/<uuid>/submit-for-approval/` | Submit / re-submit batch for review |
| POST | `/api/v1/manufacturers/batches/<uuid>/generate-serials/` | Issue serials after approval |
| POST | `/api/v1/regulatory/batches/<uuid>/reject/` | Regulator reject |
| POST | `/api/v1/regulatory/batches/<uuid>/recall/` | National recall |
| GET | `/api/v1/regulatory/batches/<uuid>/audit-trail/` | Batch regulatory audit rows |
| GET | `/api/v1/regulatory/batches/recall-affected/?batch_id=` | Pharmacies with stock for batch |
| POST | `/api/v1/regulatory/verification/lookup/` | Read-only serial lookup (no scan increment side-effects beyond logging omitted) |
| POST | `/api/v1/regulatory/verification/authenticate/` | Same engine as public verify, **authenticated regulator** |
| POST | `/api/v1/pharmacies/traceability/receive-batch/` | Receive serials + stock |
| POST | `/api/v1/pharmacies/traceability/dispense-serial/` | Dispense one serial |
| POST | `/api/v1/verification/authenticate/` | **Extended** request body (`device_id`, lat/long) |

Existing routes **unchanged** in path:

- `/api/v1/regulatory/batches/pending/`, `.../approve/`, `.../suspend/`
- `/api/v1/traceability/transactions/`, `.../record/`
- `/api/v1/verification/authenticate/` (public)

## Migrations

- `products.0004_productbatch_lifecycle_status`
- `serialization.0003_productserial_custody_fields`
- `traceability.0002_batchregulatoryaudit`

**Render:** run migrations on deploy after release:

```bash
python manage.py migrate
```

**Vercel:** redeploy frontend after backend is live so any new UI calls match API.

## Local commands

```bash
cd backend
export USE_SQLITE=1   # optional local SQLite
python manage.py check
python manage.py migrate
python manage.py test tests
```

```bash
cd frontend
npm run build
npm test
```

## Workflow (high level)

1. Manufacturer registers **product** → creates **batch** (draft / pending).
2. Manufacturer **submits** batch (audit: `submitted`).
3. Regulator **approves** or **rejects** (lifecycle + `regulator_status` + audit).
4. After approval, manufacturer **generates serials** (lifecycle → `active`, audit `serials_issued`).
5. Supply chain records **movements** via existing traceability transaction API.
6. Pharmacy **receives** serials (custody + inventory) → **dispenses** (custody check, dispensed flag, sale transaction).
7. Regulator **recalls** batch → verification returns **recalled**; affected pharmacies listed via recall-affected endpoint.

## Swagger / OpenAPI

Project uses **drf-spectacular**. New endpoints appear under `/api/docs/` after deploy when serializers/views are registered.

## Risks

- **Breaking change for manufacturers** who previously passed `issue_serial_count > 0` on batch create: serials must now be generated via `generate-serials` after approval.
- **Verification stricter**: batches must have `lifecycle_status` in `approved` or `active` for authentic public scans — legacy rows may need a one-off data fix (migration backfill already sets sensible defaults).
- **Performance**: `batch.refresh_from_db()` per verify adds one query — acceptable for national verification volume at current scale.

## Files touched (reference)

Backend: `apps/core/constants.py`, `products/models.py`, `products/services.py`, `products/admin.py`, `serialization/models.py`, `serialization/services.py`, `traceability/models.py`, `traceability/services.py`, `traceability/regulatory_audit.py`, `traceability/admin.py`, `traceability/api/serializers.py`, `verification/services.py`, `verification/api/serializers.py`, `verification/api/views.py`, `citizen/api/serializers.py`, `citizen/api/views.py`, `manufacturers/*`, `regulatory/*`, `pharmacies/*`, migrations, `tests/*`.

Frontend: regulator traceability page, `services/traceability.ts`, `CommandShell` nav, citizen verify UI (additive).
