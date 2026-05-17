# NPTTE Phase 3 — National Platform APIs

Additive endpoints only. All Phase 2 routes remain unchanged.

## National traceability (`/api/v1/traceability/`)

| Method | Path | Access |
|--------|------|--------|
| GET | `transactions/` | Org members / Regulators |
| POST | `transactions/record/` | Supply chain actors |
| GET | `transactions/<audit_reference>/` | Authenticated |
| GET | `recalls/` | Regulators |

## Verification (`/api/v1/verification/`)

| Method | Path | Access |
|--------|------|--------|
| POST | `authenticate/` | Public (rate limited) |
| GET | `history/` | Regulators |

## Audit forensics (`/api/v1/audit/`)

| Method | Path | Access |
|--------|------|--------|
| GET | `logs/` | Regulators (filterable) |

## Analytics (`/api/v1/analytics/`)

| Method | Path | Access |
|--------|------|--------|
| GET | `inventory/summary/` | Regulators |
| GET | `transactions/volume/` | Regulators |
| GET | `inventory/by-state/` | Regulators |
| GET | `products/top/` | Regulators |

## National dashboard (`/api/v1/dashboard/`)

| Method | Path | Access |
|--------|------|--------|
| GET | `overview/` | Regulators |

## Alerts (`/api/v1/alerts/`)

| Method | Path | Access |
|--------|------|--------|
| GET | `` | Regulators |

## Patient extensions (`/api/v1/patients/`)

| Method | Path | Access |
|--------|------|--------|
| GET/POST | `saved-medications/` | Patient |
| DELETE | `saved-medications/<uuid>/` | Patient |
| GET/POST | `refill-reminders/` | Patient |
| GET | `medication-compare/?product_ids=` | Public |

Existing patient routes (`medication-search/`, `nearby-pharmacies/`, etc.) are unchanged.
