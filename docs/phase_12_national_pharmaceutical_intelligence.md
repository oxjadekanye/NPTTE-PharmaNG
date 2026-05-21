# Phase 12 — National Pharmaceutical Intelligence & Supply Chain Engine

Additive layer on Phase 11 realtime/task infrastructure. Preserves mobile scanning (see `phase_12_mobile_scanning.md`).

## New APIs

### Intelligence
| Method | Path |
|--------|------|
| GET | `/api/v1/intelligence/medicines/` |
| GET | `/api/v1/intelligence/medicines/<uuid>/` |
| GET | `/api/v1/intelligence/manufacturers/` |
| GET | `/api/v1/intelligence/shortage-risk/` |
| GET | `/api/v1/intelligence/counterfeit-risk/` |

### Supply chain & recalls
| Method | Path |
|--------|------|
| GET | `/api/v1/traceability/supply-chain/shipments/` |
| GET | `/api/v1/traceability/supply-chain/custody/` |
| GET | `/api/v1/traceability/recall-orchestration/` |

### Pharmacy network
| Method | Path |
|--------|------|
| GET | `/api/v1/pharmacies/network/ranking/` |
| GET | `/api/v1/pharmacies/network/verified/` (public) |

### Crisis mode
| Method | Path |
|--------|------|
| GET | `/api/v1/emergency-response/crisis-mode/` |
| POST | `/api/v1/emergency-response/crisis-mode/activate/` |

### Analytics
| Method | Path |
|--------|------|
| GET | `/api/v1/analytics/scan-analytics/` |
| GET | `/api/v1/analytics/regional-trends/` |
| GET | `/api/v1/analytics/export-bundle/` |

### Mobile field workflows
| Method | Path |
|--------|------|
| POST | `/api/v1/mobile/field/seizure/` |
| POST | `/api/v1/mobile/field/customs-hold/` |
| POST | `/api/v1/mobile/field/warehouse-transfer/` |
| POST | `/api/v1/mobile/field/pharmacy-recall-ack/` |

## Web routes
- `/regulator/medicines`, `/regulator/medicines/[id]`, `/regulator/medicines/risk`
- `/regulator/manufacturers`
- `/regulator/supply-chain`
- `/command-center/recall-orchestration`
- `/executive/crisis-mode`
- `/regulator/analytics`

## Mobile routes
- `/regulator/seizure`
- Enhanced `/customs/hold` (shipment hold API)

## Services
- `backend/apps/intelligence/services/medicine_intelligence.py`
- `backend/apps/fraud_detection/services/counterfeit_engine.py`
- `backend/apps/traceability/services/supply_chain_intelligence.py`
- `backend/apps/pharmacies/services/pharmacy_network.py`

## Copilot
Existing modes: `shortage_forecast`, `hotspot_prediction`, `recall_spread_analysis`, `deployment_suggestions` — deterministic fallback only.

## Render
No new env vars. No migrations in Phase 12 (uses existing models).

## Tests
`backend/tests/test_phase12_national_pharmaceutical.py`
