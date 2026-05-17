# NPTTE Frontend Architecture (Phase 6)

## Stack

- Next.js 15 App Router
- TypeScript
- Tailwind CSS
- Zustand (auth state)
- Recharts-ready (analytics pages)
- Leaflet (threat map)
- Vitest + Testing Library

## Principles

1. **API-only** — no direct database access
2. **Additive** — does not modify backend business logic
3. **Role-aware** — `RegulatorGuard` + permission checks
4. **Realtime-ready** — SSE via `/api/v1/realtime/stream/`

## Environment

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_REALTIME_SSE_URL=http://localhost:8000/api/v1/realtime/stream/
```

## Startup

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Open http://localhost:3000
