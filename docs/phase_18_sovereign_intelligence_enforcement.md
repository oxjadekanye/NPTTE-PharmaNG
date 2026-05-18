# Phase 18 — Sovereign Intelligence & Enforcement Engine

Additive national pharmaceutical intelligence and enforcement layer on top of Phase 17 streambus/realtime infrastructure.

## Intelligence domain (`apps/intelligence`)

### Models

| Model | Purpose |
|-------|---------|
| `NationalRiskSnapshot` | Persisted national composite risk |
| `OrganisationRiskProfile` | Per-organisation integrity and risk |
| `ProductRiskProfile` | Product-level counterfeit/recall risk |
| `RegionalRiskProfile` | State/region heat and scan density |
| `IntelligenceSignal` | Correlated anomaly signals |
| `CounterfeitCluster` | Grouped suspicious serial activity |
| `IntelligenceNarrative` | Template-generated briefings |

### Scoring (deterministic, no ML)

- `calculate_national_risk()` — suspicious/invalid scans, recalls (24h)
- `calculate_organisation_risk()` — org scans, duplicates, delayed recall acks
- `calculate_product_risk()` — product-linked scans, recalls, expired batches
- `calculate_regional_risk()` — regional scan density and suspicious rate
- `calculate_counterfeit_probability()` — serial-level (delegates to ai_engine when available)
- `calculate_shortage_pressure()` — baseline + regional org density
- `calculate_recall_execution_risk()` — active campaigns and pending pharmacy acks

Each returns: `score` (0–100), `status` (green/amber/red/critical), `confidence`, `reasons`, `recommended_actions`.

### Correlation engine

`run_correlation(window_hours, suspicious_threshold)` groups suspicious scans by region and serial prefix; creates `IntelligenceSignal` and `CounterfeitCluster` records when thresholds are met.

### Narratives

Template-based `generate_narrative()` and `generate_executive_briefing()` — no external AI APIs.

## Enforcement domain (`apps/enforcement`)

### Models

| Model | Purpose |
|-------|---------|
| `EnforcementCase` | Case lifecycle (open → closed) |
| `EnforcementRecommendation` | Automated regulator recommendations |
| `EnforcementAction` | Recorded actions on a case |
| `InvestigationAssignment` | Regulator assignment |
| `EnforcementTimelineEntry` | Audit timeline |

### Automation

`process_risk_threshold()` when national/org risk score ≥ 65:

- Creates `EnforcementRecommendation`
- At score ≥ 80, opens `EnforcementCase`
- Creates operational task, activity feed item, optional org notification
- Publishes streambus events

## APIs

### Intelligence (`/api/v1/intelligence/`)

| Method | Path | Access |
|--------|------|--------|
| GET | `national-risk/` | Regulator |
| GET | `regional-risk/` | Regulator |
| GET | `product-risk/` | Regulator |
| GET | `organisation-risk/` | Regulator or linked org |
| GET | `signals/` | Regulator (all) / org (filtered) |
| GET | `clusters/` | Regulator |
| POST | `run-correlation/` | Regulator |
| GET/POST | `narratives/` | Regulator |
| GET | `executive-briefing/` | Regulator |
| GET | `national/` | Legacy Phase 10 (preserved) |
| GET | `serial-risk/` | Legacy Phase 10 (preserved) |

### Enforcement (`/api/v1/enforcement/`)

| Method | Path | Access |
|--------|------|--------|
| GET/POST | `cases/` | Regulator (POST); list filtered for org users |
| POST | `cases/<id>/assign/` | Regulator |
| GET | `recommendations/` | Regulator / org filtered |
| POST | `recommendations/<id>/accept/` | Regulator |
| POST | `recommendations/<id>/dismiss/` | Regulator |
| GET | `timeline/` | Regulator / org filtered |

## Frontend routes

| Route | UI |
|-------|-----|
| `/regulator/intelligence` | National risk dashboard |
| `/regulator/intelligence/clusters` | Counterfeit cluster cards |
| `/regulator/intelligence/narratives` | Briefing panel |
| `/regulator/enforcement` | Recommendations + timeline |
| `/regulator/enforcement/cases` | Case board |
| `/executive` | Phase 18 briefing panel (additive) |

Navigation: Command section in `frontend/src/config/navigation.ts`.

## Streambus events

- `intelligence.signal.created`
- `intelligence.cluster.detected`
- `intelligence.risk.updated`
- `enforcement.case.created`
- `enforcement.recommendation.created`
- `enforcement.case.escalated`

Published via `publish_operational_event()` with graceful fallback if Redis/bus unavailable.

## Deployment

### Render (backend)

```bash
python manage.py migrate
```

New migrations:

- `apps/intelligence/migrations/0001_initial.py`
- `apps/enforcement/migrations/0001_initial.py`

No destructive changes. Existing APIs unchanged; Phase 10 `/intelligence/national/` preserved.

### Vercel (frontend)

Standard deploy; new regulator routes are static Next.js pages under `(regulator)`.

## Limitations

- Rule-based scoring only; no ML models in this phase
- Product–scan linkage uses serial prefix heuristics
- Correlation capped at 500 scans per run for performance
- Narratives are template strings, not LLM-generated
- Enforcement “legal referral” is a placeholder type for a future phase

## Next phase recommendation

- Wire ML counterfeit models into `calculate_counterfeit_probability`
- Geo heatmap visualization for regional risk
- Workflow engine for case state transitions and SLA timers
- Ministerial PDF export via integrations layer
- Citizen-safe public risk indices (aggregated only)
