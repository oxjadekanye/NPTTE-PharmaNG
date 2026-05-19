# Phase 23 — Production Identity + Release Hardening

## Branding system

Centralized tokens:

| Platform | Path |
|----------|------|
| Mobile | `mobile/src/theme/branding.ts` |
| Web | `frontend/src/theme/branding.ts` |

Includes sovereign dark palette, alert/enforcement/intelligence colors, typography scale, spacing, icon sizes, shadows, and operational gradients.

Web CSS variables are mirrored in `frontend/src/app/globals.css`.

Asset placeholders: `assets/branding/` and `mobile/assets/branding/` (PNG for EAS + SVG sources).

## Release architecture

```
Expo app (mobile/)
  app.config.ts     — environment-aware Expo config
  eas.json          — development | preview | production profiles
  src/config/env.ts — APP_ENV + API URL resolution
```

| Environment | API default |
|-------------|-------------|
| development | `http://localhost:8000/api/v1` |
| staging | `https://nptte-backend-staging.onrender.com/api/v1` |
| production | `https://nptte-backend.onrender.com/api/v1` |

Override with `EXPO_PUBLIC_API_BASE_URL` or EAS profile `env`.

## Android release setup

1. Install EAS CLI: `npm i -g eas-cli`
2. Login: `eas login`
3. Configure project ID in `app.config.ts` → `extra.eas.projectId`
4. Internal APK (preview):

```bash
cd mobile
eas build --profile preview --platform android
```

5. Production AAB (Play Store track):

```bash
eas build --profile production --platform android
```

Signing: configure credentials via `eas credentials` (placeholders in repo — no secrets committed).

Package: `ng.gov.nptte.mobile`

## iOS preparation

- Bundle ID: `ng.gov.nptte.mobile`
- Tablet supported
- Permission strings in `app.config.ts` Info.plist
- Production submit placeholders in `eas.json` (not published)
- Simulator build via `development` profile

## Environment management

Copy `mobile/.env.example` → `.env.local` for local dev.

EAS profiles inject `APP_ENV` and `EXPO_PUBLIC_*` at build time.

## Operational UX strategy

- `Skeleton` / `SkeletonCard` — professional loading
- `OperationalStates` — empty, degraded network, sync conflict
- `OperationalCard` — enforcement/intelligence variants
- `ScreenShell` — branded typography and spacing
- Splash: native `expo-splash-screen` + in-app `LandingBootSplash` with readiness pulse

## Security hardening

| Feature | Implementation |
|---------|----------------|
| Token refresh | `session-security.ts` → `/auth/refresh/` |
| Session expiry | JWT `exp` in SecureStore; hydrate refresh |
| Secure logout | Blacklist refresh + clear tokens + offline/evidence queues |
| API timeout | 30s default (`API_TIMEOUT_MS`) |
| Screenshot block | `ScreenProtection` placeholder |
| 401 handling | Auto-refresh then redirect `/login` |

## Internal APK distribution

See `docs/mobile_internal_apk_distribution.md` for regulator field testing workflow.

## Deployment readiness

| Item | Status |
|------|--------|
| Brand tokens | Ready |
| EAS profiles | Ready (preview + production) |
| Placeholder icons/splash | Ready — replace with final artwork |
| Permissions copy | Ready |
| Session security | Ready |
| Play Store listing | Not started |
| iOS App Store | Not started |
| FCM production push | Not started |
| Final app signing keys | Configure in EAS |

## Remaining blockers before Play Store

1. Replace placeholder PNG brand assets with official NAFDAC/NPTTE artwork
2. Set real `EAS_PROJECT_ID` and configure signing credentials
3. Privacy policy URL + Play Data Safety form
4. Production FCM + notification backend
5. Penetration test on mobile token storage and refresh flow
6. Physical device QA matrix (Samsung mid-range + flagship)
7. Remove or gate any demo-only UI labels in production builds
