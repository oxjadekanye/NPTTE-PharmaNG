# Regulator Command Center UI

## Access

1. Start backend: `cd backend && python manage.py runserver`
2. Start frontend: `cd frontend && npm run dev`
3. Sign in at `/login` with a regulator account (e.g. `nptte_admin` or NAFDAC role)

## Modules

- **Overview** (`/regulator`) — live metrics, fraud, verification traffic
- **Command** (`/command-center`) — disruptions and interventions
- **Threat map** — Leaflet counterfeit hotspots
- **Incidents** — national incident table
- **Approvals** — organisation onboarding queue
- **Emergency** — crisis distribution activation
- **Analytics** — national summary, flow, heatmaps
