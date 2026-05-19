# NPTTE PharmaNG — Mobile (Phase 21–22)

Expo (React Native) field operations app consuming the **existing** Django REST APIs. No duplicated backend logic.

See [docs/phase_22_mobile_operational_maturity.md](../docs/phase_22_mobile_operational_maturity.md) for device trust, biometrics, evidence, and realtime details.

## Stack

- **Expo SDK 52** + **expo-router** (file-based navigation)
- **TypeScript**
- **Zustand** + AsyncStorage (offline + evidence queues)
- **expo-secure-store** (JWT tokens)
- **expo-camera** (QR / barcode) + **expo-haptics**
- **expo-local-authentication** (biometric unlock)
- **expo-image-picker** / **expo-image-manipulator** (evidence)
- **expo-notifications** (push orchestration foundation — not published)

## Configure API

Set production API URL before running on device:

```bash
export EXPO_PUBLIC_API_BASE_URL=https://your-render-service.onrender.com/api/v1
```

Or edit `app.json` → `expo.extra.apiBaseUrl`.

## Run locally

```bash
cd mobile
npm install
npm run start
```

Press `i` for iOS simulator or `a` for Android emulator. Use Expo Go for quick device testing.

## Scripts

| Command | Purpose |
|---------|---------|
| `npm run start` | Expo dev server |
| `npm run typecheck` | TypeScript check |
| `npm test` | Vitest (role routing) |

## Role homes

After staff login, users route to:

| Role | Path |
|------|------|
| Citizen (guest) | `/citizen` |
| Pharmacy | `/pharmacy` |
| Regulator | `/regulator` |
| Customs | `/customs` |
| Warehouse | `/warehouse` |
| Executive | `/executive` |

## Offline

Scans queue locally when offline (staff roles). Sync via `POST /scanning/sync-pending/`. See **Offline queue** screen.

## Not published

This foundation is **not** submitted to App Store / Play Store. Native build profiles (EAS) can be added in Phase 21+.

See `docs/phase_21_mobile_foundation.md`.
