# Phase 21 — Native Mobile App Foundation

## Framework

**Expo SDK 52** (React Native 0.76) with **expo-router** — separate from the Next.js Vercel web app under `frontend/`.

## Architecture

```
mobile/
  app/           # expo-router screens (by role)
  src/
    services/    # API clients (mirror web contracts)
    store/       # auth + offline queue
    hooks/       # network, scan submit, offline sync
    components/  # scanner, scan workflow, shell
    lib/         # role routing
```

All data flows through existing `/api/v1/` endpoints:

- Auth: `/auth/login/`, `/auth/profile/`, `/auth/permissions/`
- Scanning: `/scanning/ingest/`, `/scanning/sync-pending/`, `/scanning/history/`
- Citizen: `/public/verify/`, `/public/recalls/`, `/public/report-counterfeit/`
- Mobile devices: `/mobile/devices/register/` (push placeholder)
- Executive: `/command-orchestration/*`, `/copilot/executive-briefing/`

No backend changes required for Phase 21 foundation.

## Screens by role

### Citizen (no login)
- Scan verify, manual lookup, recalls, counterfeit report

### Pharmacy
- Receive, dispense, recalls info, offline queue

### Regulator field
- Inspection scan, checklist, evidence placeholder, AI enforcement note, case info

### Customs
- Verify shipment, batch scan, hold/escalate guidance

### Warehouse
- Receive, transfer, cold-chain info, custody timeline (scan history)

### Executive
- National readiness, urgent alerts, AI briefing (manual), regional summary

## Offline-first

- `useOfflineQueue` persists up to 200 scans in AsyncStorage
- `useOfflineSync` calls `/scanning/sync-pending/` when online
- `OfflineBanner` on all staff flows

## Camera scanning

- `BarcodeScanner` uses `expo-camera` `CameraView` with QR + barcode types
- Manual serial fallback on all scan workflows
- Permission prompts per platform (see `app.json` Info.plist / Android permissions)

## Push foundation

- `initPushFoundation()` requests notification permission and registers device
- Full push delivery (recalls, tasks, suspicious scans) deferred to Phase 21+

## Build instructions

```bash
cd mobile && npm install
npm run typecheck
npm test
npm run start
```

For production binaries (future):

```bash
npx eas build --platform all --profile preview
```

Not run in Phase 21 — **do not publish** yet.

## Remaining risks

- Physical device testing required for camera performance on low-end Android
- `localhost` API URL will not work on real devices — must set `EXPO_PUBLIC_API_BASE_URL`
- Push notifications need EAS credentials + backend push provider
- Evidence upload and full investigation room are web-first
- Executive/regulator complex workflows remain on web command platform
- No automated Detox/E2E yet — only unit tests for role routing
