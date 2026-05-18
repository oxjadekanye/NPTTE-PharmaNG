# Phase 11 — Production Hardening & Pilot Launch Preparation

Additive pilot operations layer. No auth/RBAC/CORS/Render/Vercel config changes. No destructive migrations.

## Features added

1. **Pilot Readiness dashboard** — health, DB, modules, risks, readiness score, demo checklists
2. **Onboarding workflow board** — templates per org type + live/pilot entries
3. **Demo Control Center** — seed/clear only `pilot_demo` tagged records; client feed reset
4. **API Readiness** — catalog of API groups, auth, health hints
5. **Security hardening display** — JWT/CORS/RBAC/audit status (no secrets)
6. **Performance readiness** — volume and growth indicators
7. **Documentation center** — in-app pilot guides
8. **Pilot Presentation** — public `/pilot` stakeholder story route
9. **Grouped navigation** — Command / Operations / Ecosystem / Governance sections

## Routes added

| Route | Access |
|-------|--------|
| `/regulator/pilot-readiness` | Regulator JWT |
| `/regulator/onboarding` | Regulator JWT |
| `/regulator/demo-control` | Regulator JWT |
| `/regulator/api-readiness` | Regulator JWT |
| `/regulator/docs` | Regulator JWT |
| `/pilot` | Public presentation |

## APIs added (`/api/v1/pilot/`)

- `GET readiness/`
- `GET onboarding-workflows/`
- `GET|POST demo-control/`
- `GET api-readiness/`
- `GET security/`
- `GET performance/`

## Migrations

**None** — Phase 11 uses existing models and metadata tagging for demo data.

## Pilot demo flow

1. Open `/pilot` for stakeholder narrative
2. Regulator login → **Pilot Readiness** for score and checklists
3. Run **Demo Control** seed actions before demo (tagged DEMO only)
4. Walk **Documentation** guides per audience
5. Execute regulator/pharmacy/manufacturer/citizen paths from checklists
6. **API Readiness** for integration Q&A

## Deployment

### Render

- Deploy backend (no new env vars)
- No migrate required for Phase 11

### Vercel

- Redeploy frontend
- `NEXT_PUBLIC_API_BASE_URL` unchanged

## Risks

- Demo seed creates real DB rows tagged `pilot_demo` — use **Clear tagged demo data** after demos
- Simulated intelligence remains alongside live APIs (by design)
- Onboarding workflow board shows DEMO placeholders when no real onboarding rows exist

## Next phase recommendation

**Phase 12 — Pilot execution:** connect onboarding UI to live submission APIs, field scanner apps, regulator approval SLAs, and production analytics export for NAFDAC reporting.
