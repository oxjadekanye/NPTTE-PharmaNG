# Phase 22 — Mobile Operational Maturity + Device Intelligence

## Overview

Phase 22 extends the Expo mobile app (`mobile/`) and shared Django `/api/v1/mobile/` APIs into sovereign field-operational tools: device trust, biometrics, advanced scanning, evidence capture, realtime feeds, AI field assistant, offline resilience, and push orchestration — without duplicating backend business logic or forking web workflows.

## Device trust

**Client:** `mobile/src/services/device-trust.ts`

- Stable device fingerprint (model, OS, application id)
- Emulator/root placeholders (`expo-device`)
- `POST /mobile/devices/trust/` on login
- `POST /mobile/devices/heartbeat/` for last-seen and optional session token rotation

**Server:** `backend/apps/mobile/services/device_trust.py`

Tracks: `trusted_status`, `device_risk_level`, `fingerprint_hash`, `platform`, `assigned_role_code`, `suspicious_device`, `last_heartbeat_at`, `biometric_capable`.

## Biometric flow

**Package:** `expo-local-authentication`

- Toggle in **Settings** (`/settings`)
- `BiometricGate` wraps the app stack after first login when enabled
- Fallback to password via `/login`
- Refresh tokens remain in `expo-secure-store` (Phase 21)

## Advanced scanning

**Component:** `AdvancedScanWorkflow`

- Continuous / rapid warehouse mode
- Haptic feedback (`expo-haptics`)
- Duplicate scan suppression
- Confidence indicator from scan risk score
- Manual AI explain (regulator) via `/mobile/copilot/`
- Modes: `standard`, `rapid`, `inspection`, `customs`

Citizen flow keeps lightweight `ScanWorkflow` (no auth).

## Evidence handling

**Client:** `EvidenceCapture`, `evidence-queue` store, `useEvidenceSync`

- Camera capture + JPEG compression (`expo-image-manipulator`)
- GPS stamping when permitted
- Offline queue with retry on reconnect
- `POST /mobile/evidence/`, `POST /mobile/evidence/sync/`

Types: `inspection`, `customs_seizure`, `warehouse_breach`, `counterfeit` (extensible).

## Offline strategy

- Scan queue: priority (inspection > default), exponential backoff in `useOfflineSync`
- Evidence queue: separate persisted store
- **Sync health** screen: `/sync-health` — pending/failed diagnostics
- **OfflineStatusBar** on all `ScreenShell` screens
- Last sync timestamps on both queues

## Realtime mobile orchestration

**Hook:** `useMobileRealtime` — polls `GET /mobile/realtime/feed/?channel=&since_sequence=` every 20s when online (SSE-ready backend; mobile uses lightweight polling).

Channels: `officer_tasks`, `executive`, `warehouse`, `investigation`.

Local notifications for recall / escalation / task events via `push-orchestration`.

## AI mobile assistant

**Service:** `mobile-ai.ts` → `POST /mobile/copilot/`

- Manual trigger only (buttons on scan, inspection checklist, executive briefing)
- Wraps existing copilot reasoning — no automatic enforcement
- Regulator-gated on server; deterministic fallback when denied

## Push strategy

**Service:** `push-orchestration.ts`

- Role-based Android notification channels
- User preferences in AsyncStorage (recalls, enforcement, suspicious scans, regional, tasks, executive)
- `initPushOrchestration` after login
- Full FCM/APNs delivery deferred — local alerts for realtime poll hits

## Field workflows

| Role | Enhancements |
|------|----------------|
| Regulator | Checklist engine, evidence on inspect, field activity log |
| Customs | Hold workflow + AI recommendation, customs scan mode |
| Warehouse | Rapid scan, cold-chain AI summary, realtime alerts |
| Executive | Live feed hook, AI briefing, national snapshot |
| All staff | Settings, sync health, device trust on login |

## Operational audit

Server: `MobileOperationalAudit` — device, actor, action, GPS, evidence linkage.

Client timeline: `/field-activity` → `GET /mobile/audit/timeline/`

## Performance strategy

- Image resize/compress before upload
- Incremental realtime merge (no full-screen rerenders)
- Skeleton-ready screen shells
- Lazy route loading via expo-router file routes
- Queue caps: 200 scans, 50 evidence items

## Deployment notes

```bash
cd mobile && npm install
npm run typecheck && npm test
npm run start
```

```bash
cd backend
python manage.py migrate
USE_SQLITE=1 python manage.py test tests.test_phase22_mobile
```

Set `EXPO_PUBLIC_API_BASE_URL` for physical devices. EAS build credentials required for store distribution.

## Remaining limitations

- Jailbreak/root detection placeholders (integrate native module)
- Video evidence placeholder only
- Mobile copilot regulator-only; pharmacy/customs use deterministic scan outcomes
- SSE not wired on mobile — polling fallback
- Push is local + channel foundation; no production FCM/APNs pipeline
- Officer signature capture deferred to web enforcement
- Detox/E2E device tests not yet added
