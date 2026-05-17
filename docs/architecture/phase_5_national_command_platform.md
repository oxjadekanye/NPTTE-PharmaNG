# Phase 5 — National Pharmaceutical Command Platform

## Overview

Phase 5 transforms NPTTE PharmaNG into a **national pharmaceutical digital infrastructure** with regulator command operations, citizen verification, event streaming, and enterprise analytics — all implemented as **additive Django apps** without breaking Phase 1–4 APIs.

## New modules

| App | Purpose |
|-----|---------|
| `command_center` | National incidents, threat assessments, live command APIs |
| `events` | Append-only event stream (Redis/Kafka-ready) |
| `market_intelligence` | Price monitoring, manipulation detection |
| `citizen` | Public verification, counterfeit reporting, trusted pharmacies |
| `onboarding` | Enterprise organisation approval workflows |
| `emergency_response` | Crisis distribution and emergency protocols |
| `national_analytics` | Nationwide aggregation engine |
| `mobile` | Device registration and offline sync tokens |

## Key API routes (additive)

- `/api/v1/command-center/live-overview/`
- `/api/v1/command-center/threat-map/`
- `/api/v1/public/verify/`
- `/api/v1/onboarding/`
- `/api/v1/analytics/national-summary/` (extends existing analytics namespace)
- `/api/v1/events/replay/`
- `/api/v1/mobile/devices/register/`

## Security

- `SecurityThreatLog` for suspicious activity
- Citizen endpoints: `citizen` throttle scope (30/min)
- Command center: `command` throttle scope
- HMAC API signature verification in `apps.core.security`

## Deployment

Run migrations after deploy:

```bash
python manage.py migrate
python manage.py seed_roles
```

Optional: set `REDIS_URL` for cache, event pub/sub, and aggregation caching.
