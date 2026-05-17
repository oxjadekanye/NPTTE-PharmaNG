# MVP Phase 1 — Backend Foundation

**Status:** In progress  
**Goal:** Establish a government-grade Django foundation that future modules can extend without rework.

## Deliverables

- [x] Monorepo directory structure
- [x] Django project with environment-based PostgreSQL / SQLite
- [x] Thirteen domain applications with docstrings
- [x] Foundational models (18 entities)
- [x] Shared `NPTTEBaseModel` with UUID, audit, lifecycle, metadata
- [x] Django admin registration
- [x] Patient medication search service placeholders
- [x] Architecture, database, API, security documentation
- [ ] Initial migrations applied in target environments
- [ ] Seed data scripts for organisation types and roles (Phase 1b)

## Out of scope (explicit)

| Item | Target phase |
|------|----------------|
| DRF API endpoints | Phase 2 |
| JWT / OAuth | Phase 2 |
| Next.js web dashboard | Phase 2–3 |
| Flutter mobile apps | Phase 3 |
| Real-time inventory sync | Phase 2 |
| PostGIS geospatial search | Phase 2 |
| SMS / email notifications | Phase 2 |
| AI fraud detection | Phase 4 |
| Hyperledger Fabric | Phase 4 |
| FastAPI microservices | As needed per load |

## Success criteria

1. `python manage.py check` passes with no issues
2. Migrations apply cleanly on PostgreSQL and SQLite
3. Superuser can manage all entities via admin
4. Documentation accurately describes module boundaries
5. No circular import errors between apps

## Phase 2 preview

- DRF serializers and viewsets per app
- `/api/v1/patients/medication-search/` endpoint wired to `patients.services`
- Organisation membership model
- Inventory upload API for pharmacies
- OpenAPI documentation

## Risks and mitigations

| Risk | Mitigation |
|------|------------|
| Geospatial search at scale | Plan PostGIS migration; keep service interface stable |
| PII exposure in patient search | Consent flags, authentication, rate limits in Phase 2 |
| Model sprawl | Strict app boundaries documented in module map |
| Premature blockchain/AI | Placeholder dirs only; no production coupling |

## Team handoff checklist

- [ ] Copy `backend/.env.example` → `backend/.env`
- [ ] Provision PostgreSQL database `nptte`
- [ ] Run migrations and create superuser
- [ ] Review `docs/security/security_principles.md` before any public endpoint
