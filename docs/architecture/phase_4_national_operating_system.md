# NPTTE Phase 4 — National Pharmaceutical Operating System

## Vision

NPTTE PharmaNG operates as sovereign national pharmaceutical infrastructure — not a pharmacy app. Phase 4 adds manufacturer ecosystems, sovereign verification, logistics chain-of-custody, prescription intelligence, regulator command center APIs, AI-ready heuristics, emergency monitoring, and cross-border foundations.

## Module map (additive)

| Module | Responsibility |
|--------|----------------|
| `manufacturers` | Sites, licenses, GMP, batches, recalls, serial issuance |
| `verification` | Sovereign authenticate + VerificationScanLog |
| `logistics` | Shipments, checkpoints, cold chain, delivery |
| `prescriptions` | E-prescriptions, dispensing, refill risk |
| `distributors` | Profiles + warehouses |
| `alerts` | National alerts + escalations |
| `ai_engine` | Risk signals, forecasts, organisation scores |
| `emergency` | Epidemic medicine watchlist |
| `international` | Import/export manifests, border verification |
| `national_dashboard` | Command center metrics |

## Sovereign serial format

```
NG-NPTTE-{PRODUCT}-{YEAR}-{SEQUENCE}
Example: NG-NPTTE-PARACETAMOL-2026-000000001
```

## Verification outcomes

`authentic`, `counterfeit_suspected`, `recalled`, `expired`, `duplicate_scan_detected`, `invalid_serial`, `unregistered_product`

## Regulator command center

- `GET /api/v1/dashboard/overview/` (unchanged)
- `GET /api/v1/dashboard/national-overview/`
- `GET /api/v1/dashboard/counterfeit-map/`
- `GET /api/v1/dashboard/shortages/`
- `GET /api/v1/dashboard/supply-chain/`
- `GET /api/v1/dashboard/high-risk-organisations/`

## RBAC

All existing `RoleCode` values preserved. Phase 4 adds no breaking role changes.

## Scale hooks

- `REDIS_URL` / `CELERY_BROKER_URL` environment variables
- `apps.core.cache` abstraction
- Database indexes on high-volume tables
- Partition-ready transaction models (future)
