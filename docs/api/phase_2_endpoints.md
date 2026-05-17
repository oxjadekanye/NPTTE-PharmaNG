# NPTTE API v1 — Phase 2 Endpoints

Base URL: `/api/v1/`

Authentication: `Authorization: Bearer <access_token>` unless marked public.

## Health

| Method | Path | Auth |
|--------|------|------|
| GET | `/api/v1/health/` | Public |

## Authentication

| Method | Path | Auth |
|--------|------|------|
| POST | `/api/v1/auth/register/` | Public |
| POST | `/api/v1/auth/login/` | Public |
| POST | `/api/v1/auth/refresh/` | Public |
| POST | `/api/v1/auth/verify/` | Public |
| POST | `/api/v1/auth/logout/` | JWT |
| GET/PATCH | `/api/v1/auth/profile/` | JWT |
| POST | `/api/v1/auth/password/change/` | JWT |
| GET | `/api/v1/auth/permissions/` | JWT |

## Pharmacies

| Method | Path | Auth |
|--------|------|------|
| GET/PATCH | `/api/v1/pharmacies/profile/` | Pharmacy staff / Regulator |
| GET/POST | `/api/v1/pharmacies/inventory/` | Pharmacy inventory manager |
| GET/PATCH/DELETE | `/api/v1/pharmacies/inventory/<uuid>/` | Pharmacy inventory manager |
| GET | `/api/v1/pharmacies/availability/` | Pharmacy staff |

## Patients

| Method | Path | Auth |
|--------|------|------|
| GET/PATCH | `/api/v1/patients/profile/` | Patient |
| GET | `/api/v1/patients/products/search/` | Public |
| POST | `/api/v1/patients/medication-search/` | Public (consent if patient JWT) |
| GET | `/api/v1/patients/nearby-pharmacies/` | Public |
| GET | `/api/v1/patients/search-history/` | Patient / Regulator |
| GET | `/api/v1/patients/search-history/<uuid>/` | Patient / Regulator |

## Documentation

| Path | Description |
|------|-------------|
| `/api/docs/` | Swagger UI |
| `/api/redoc/` | ReDoc |
| `/api/schema/` | OpenAPI schema |
