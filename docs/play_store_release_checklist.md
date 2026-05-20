# Google Play Store Release Checklist — NPTTE PharmaNG

**Status:** Preparation only — do not submit until regulator sign-off.

## Build readiness

- [ ] Preview APK tested on Samsung device (`eas build --profile preview`)
- [ ] Production AAB (`eas build --profile production`)
- [ ] Adaptive icon: `mobile/assets/branding/adaptive-icon-foreground.png`
- [ ] Splash: `mobile/assets/branding/splash-logo.png`, black background
- [ ] Version: `app.config.ts` `version` + EAS `autoIncrement` for production
- [ ] Package ID: `ng.gov.nptte.mobile` (unchanged)
- [ ] Release channel: `production` in `eas.json`

## Screenshots (phone + optional 7" tablet)

- [ ] Landing / citizen verification
- [ ] Regulator scan workflow
- [ ] Evidence capture
- [ ] Executive briefing (web or tablet companion if listed)
- [ ] Offline queue status

## Legal & policy

- [ ] Privacy policy URL (government-hosted)
- [ ] Data safety form: location, camera, photos, device IDs
- [ ] Permission rationale strings match `app.config.ts` InfoPlist / Android permissions
- [ ] Content rating questionnaire (government / health app)

## Permissions explanations (Play Console)

| Permission | User-facing reason |
|------------|-------------------|
| Camera | Scan serial numbers and capture enforcement evidence |
| Location | Anchor field scans to verified coordinates |
| Photos | Attach evidence to cases |
| Notifications | Operational alerts and recall notices |
| Biometric | Secure unlock for regulator sessions |

## Security (pre-submit)

- [ ] Sentry DSN in EAS secrets (when approved)
- [ ] Screenshot protection on sensitive screens (`MobileSecurity`)
- [ ] Session expiry validated on resume
- [ ] No demo credentials in production build copy

## Post-launch

- [ ] Internal testing track → closed pilot → production rollout
- [ ] Monitor crash-free sessions and ANR rate in Play Console
