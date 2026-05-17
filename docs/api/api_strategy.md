# API Strategy

## Overview

NPTTE will expose a **versioned REST API** via **Django REST Framework (DRF)** as the primary integration surface for web, mobile, and partner systems. High-throughput or streaming workloads may later use **FastAPI** services behind the same API gateway.

Phase 1 establishes models and project configuration only—**no public API routes** are registered yet.

## Versioning

- URL prefix: `/api/v1/`
- Breaking changes require `/api/v2/` with deprecation policy communicated to integrators
- OpenAPI schema generated via `drf-spectacular` (planned Phase 2)

## Authentication (planned)

| Method | Use case |
|--------|----------|
| Session | Django admin, internal tools |
| JWT (access + refresh) | Web and mobile clients |
| API keys | B2B supply chain integrations (scoped per organisation) |
| mTLS | Government agency back-end integrations |

## Authorisation model

1. **Platform roles** (`accounts.Role`) — coarse permissions
2. **Organisation membership** (future) — row-level scope to one organisation
3. **Regulator elevation** — `is_regulator` flag refined to policy engine
4. **Patient self-service** — access limited to own profile and search history

Permission classes will live in `apps.core.permissions` and per-app `permissions.py` modules.

## Endpoint groups (planned)

| Prefix | Audience | Examples |
|--------|----------|----------|
| `/api/v1/auth/` | All | Login, refresh, password reset |
| `/api/v1/organisations/` | Regulators, admins | CRUD, accreditation |
| `/api/v1/products/` | Manufacturers, regulators | Product catalogue |
| `/api/v1/inventory/` | Pharmacies | Stock upload, availability |
| `/api/v1/patients/search/` | Patients (public/authenticated) | Medication availability by location |
| `/api/v1/verify/` | Public | QR serial lookup |
| `/api/v1/regulatory/` | Regulators | Alerts, inspections |
| `/api/v1/audit/` | Regulators (read-only) | Audit query |

## Patient medication search API (planned shape)

```
POST /api/v1/patients/medication-search/
{
  "product_id": "uuid",
  "latitude": 6.5244,
  "longitude": 3.3792,
  "radius_miles": 5
}
```

Response: ranked list of pharmacies with distance, stock quantity, and opening hours. Requires patient consent flag on profile for authenticated users.

## Pagination, filtering, ordering

- Default page size: 25 (configured in `REST_FRAMEWORK`)
- Filter backends: `django-filter` (planned)
- Sensitive fields excluded via serializers per role

## Rate limiting & abuse protection

- Public verification and search endpoints: strict rate limits per IP
- Authenticated pharmacy inventory updates: organisation quotas
- WAF and API gateway in production (`infrastructure/` phase)

## Error format

Consistent JSON envelope:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Human-readable summary",
    "details": {}
  }
}
```

## Non-goals (Phase 1)

- GraphQL
- gRPC (except possible internal FastAPI)
- Webhook delivery (notifications phase 2+)
