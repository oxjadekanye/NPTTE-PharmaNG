# Mobile Real Device Test Plan (Samsung Android focus)

## Target devices

- Primary: Samsung Galaxy A/M series (Android 12+)
- Secondary: Pixel 6+ for regression

## Pre-flight

1. Install preview APK: `cd mobile && npx eas-cli build --profile preview --platform android`
2. Seed backend: `USE_SQLITE=1 python manage.py seed_demo_data`
3. Confirm API: `EXPO_PUBLIC_API_BASE_URL` → production Render URL on preview builds

## Test matrix

| # | Scenario | Steps | Pass criteria |
|---|----------|-------|---------------|
| 1 | APK install | Sideload or internal track | App opens to landing, no white flash > 500ms |
| 2 | Login speed | `nptte_admin` / `NptteAdmin2026!` | Home < 4s on LTE |
| 3 | Scanner | Regulator inspect rapid mode | Debounced scans, torch toggles, no camera freeze after 20 scans |
| 4 | Offline | Airplane mode → scan → queue | Queue increments; toast warns offline |
| 5 | Evidence | Capture 2 photos offline → online | Photos sync; queue drains |
| 6 | AI copilot | Regulator case screen copilot | Response or graceful error toast |
| 7 | Realtime | Regulator home 2 min | Feed updates without duplicate notifications |
| 8 | QA dashboard | Long-press logo 3s | Metrics, queues, version visible |
| 9 | Simulation | QA → seed incident | Toast + optional local notification |
| 10 | Rotation | Rotate during scan | Camera recovers or restarts cleanly |
| 11 | Background | Background 30s → resume | Session intact; biometric gate if enabled |
| 12 | Memory | 15 min mixed use | No OOM; no progressive slowdown |
| 13 | Battery | 30 min field simulation | < 8% drain vs baseline (record manually) |

## Command dashboards (web, same session)

- Executive briefing loads with skeleton, no layout thrash
- Command center wallboard patches batch without FPS collapse

## Failure logging

- Enable QA mode and note API avg latency + crash buffer (`CrashReporting.getRecent()` in dev logs)
- Capture logcat for native crashes

## Sign-off

| Role | Name | Date | Result |
|------|------|------|--------|
| Field QA | | | |
| Regulator ops | | | |
| Engineering | | | |
