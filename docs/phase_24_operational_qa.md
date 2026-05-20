# Phase 24 — Real Device Operational QA & Production Stabilization

## Scope

Additive production-safe hardening across mobile field operations, web command surfaces, and QA instrumentation. No backend architecture changes, no Expo SDK upgrade, and no breaking changes to explorer, streambus, copilot, or existing APIs.

## 24A — QA Infrastructure (Mobile)

| Capability | Location |
|------------|----------|
| Global error boundary | `mobile/src/components/ErrorBoundary.tsx` |
| Screen fallback UI | `mobile/src/components/ScreenErrorFallback.tsx` |
| API interceptors + latency | `mobile/src/services/api-client.ts` |
| Operational toasts | `mobile/src/store/operational-toast-store.ts`, `OperationalToast.tsx` |
| Offline degradation | `useNetwork` → `setApiNetworkOnline` |
| Retry UI component | `mobile/src/components/RetryPanel.tsx` |
| Crash reporting abstraction | `mobile/src/services/crash-reporting.ts` |
| Performance monitor | `mobile/src/services/performance-monitor.ts` |
| QA dashboard (long-press logo 2.8s) | `mobile/app/qa-dashboard.tsx` |

## 24B — Mobile Stability

- **Startup:** deferred ops after auth hydrate; splash hidden after hydrate; performance cold-boot marks.
- **Navigation:** `useSafeNavigation` prevents duplicate `router.replace` during login/boot.
- **Scanner:** debounce, torch toggle, camera lifecycle cleanup, scan timing metrics.
- **Offline:** queue rehydration validation; evidence sync exponential backoff.
- **Evidence:** stronger JPEG compression, failed upload re-queue.

## 24C — Realtime & Command

- **Mobile:** deduplicated realtime feed by `sequence_number`.
- **Web:** patch batching via `requestAnimationFrame`; duplicate scope/target suppression in patch store.

## 24D — Operational Simulation (QA only)

`mobile/src/services/operational-simulation.ts` calls existing `/pilot/demo-control/` endpoints (regulator JWT) and local notifications. Available only when QA mode is unlocked.

## 24E — Play Store Preparation

- Checklist: `docs/play_store_release_checklist.md`
- Security placeholders: `mobile/src/services/mobile-security.ts`

## 24F — Samsung Android Validation

See `docs/mobile_real_device_test_plan.md`.

## Verification

```bash
cd mobile && npm run typecheck && npm test
cd backend && python manage.py check
USE_SQLITE=1 python manage.py test tests
```

## Production Readiness (honest)

| Area | Status |
|------|--------|
| Core mobile flows | Ready for internal APK / pilot |
| Crash reporting | Abstraction only — wire Sentry DSN in EAS |
| Memory sampling | Placeholder |
| Root/jailbreak | Placeholder |
| Play Store | Checklist prepared; not submitted |
| Samsung soak test | Requires physical device run per test plan |

## Remaining bottlenecks

1. Mobile realtime still polls every 20s (acceptable per spec; SSE on mobile deferred).
2. Native screenshot/root modules not integrated.
3. Command room map layers still heavy on low-end browsers without device profiling.
4. Full streambus-driven simulation for all six scenarios requires regulator session on device.
