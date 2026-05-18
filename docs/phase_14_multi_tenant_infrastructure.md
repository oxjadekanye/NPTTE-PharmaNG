# Phase 14 — Multi-Tenant Organisation Infrastructure

Additive sovereign tenancy layer for NPTTE PharmaNG. Existing APIs, demo systems, and citizen verification remain unchanged.

## Tenancy model

- **Organisation** — tenant boundary (`organisations.Organisation`)
- **OrganisationMembership** — user ↔ organisation ↔ role (`apps.tenancy`)
- **User.organisation** — primary org mirror (backward compatible)
- **Regulator override** — national visibility; optional `X-NPTTE-Organisation-Context` header or `?organisation_id=` for scoped inspection
- **TenantAccessLog** — denied / suspicious cross-tenant attempts

## Organisation roles (Phase 14 codes)

| Code | Purpose |
|------|---------|
| `MANUFACTURER_ADMIN` | Manufacturer tenant admin |
| `DISTRIBUTOR_ADMIN` | Distributor admin |
| `WAREHOUSE_ADMIN` | Warehouse admin |
| `PHARMACY_ADMIN` | Pharmacy admin |
| `HOSPITAL_ADMIN` | Hospital admin |
| `CUSTOMS_ADMIN` | Customs admin |
| `ORGANISATION_STAFF` | Limited staff |

Legacy codes (`MANUFACTURER`, `DISTRIBUTOR`, regulators, etc.) remain valid.

## Onboarding flow

1. **Public apply** — `POST /api/v1/tenancy/onboarding/apply/` (creates org + `OrganisationOnboarding` draft, CAC/licence metadata)
2. **Submit** — `POST /api/v1/tenancy/onboarding/{id}/submit/`
3. **Regulator queue** — `GET /api/v1/tenancy/regulator/approval-queue/`
4. **Approve / reject** — `/api/v1/tenancy/regulator/approve/{id}/`, `reject/{id}/`
5. **Suspend / reactivate** — `/api/v1/tenancy/regulator/suspend/{org_id}/`, `reactivate/{org_id}/`

Frontend: `/onboarding/apply`, `/regulator/tenant-approvals`

## Invitations

- `POST /api/v1/tenancy/invitations/` — invite by email + role
- `POST /api/v1/tenancy/invitations/{id}/resend/`, `revoke/`
- `POST /api/v1/tenancy/invitations/accept/` — token acceptance

## Tenant APIs

| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/tenancy/context/current/` | Active org + memberships |
| `POST /api/v1/tenancy/context/switch/` | Regulator context switch (audited) |
| `GET /api/v1/tenancy/dashboard/` | Tenant-scoped KPIs |
| `GET /api/v1/tenancy/memberships/` | Membership list |

## Security model

- `TenantContextMiddleware` sets `request.nptte_organisation_id`
- `filter_queryset_for_tenant()` for operational querysets (e.g. scan history)
- `HasTenantOrganisationAccess` blocks cross-tenant body/query org IDs
- Regulators bypass tenant filters unless context header narrows view

## Deployment

1. **Render:** `python manage.py migrate` (applies `tenancy.0001_initial`)
2. **Roles:** run `python manage.py seed_roles` to upsert new role codes (or create via admin)
3. **Vercel:** redeploy frontend; no new env vars

## Demo / pilot safety

- `traceability_demo` and `pilot_demo` tags untouched
- Citizen `/public/verify/` unchanged
- Simulated intelligence bus unchanged
