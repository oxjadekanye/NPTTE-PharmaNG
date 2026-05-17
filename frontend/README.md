# NPTTE PharmaNG Frontend

National regulator command center and citizen verification portal.

## Commands

```bash
npm install
npm run dev      # http://localhost:3000
npm run build
npm run test
```

## Routes

- `/` — landing
- `/login` — regulator JWT auth
- `/regulator` — national overview
- `/command-center` — live command metrics
- `/command-center/threat-map` — Leaflet heatmap
- `/command-center/incidents` — active incidents
- `/command-center/approvals` — onboarding queue
- `/emergency-ops` — crisis activation
- `/regulator/analytics` — national analytics
- `/citizen` — public verification

Requires backend at `NEXT_PUBLIC_API_BASE_URL` (default `http://localhost:8000/api/v1`).
