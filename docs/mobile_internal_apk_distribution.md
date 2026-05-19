# Internal APK Distribution — NPTTE PharmaNG Mobile

## Generate internal APK

```bash
cd mobile
npm install
eas login
eas build --profile preview --platform android
```

Download the APK from the EAS build dashboard when complete.

## Install on Samsung / Android devices

1. Enable **Install unknown apps** for your file manager or browser
2. Transfer APK via USB, email, or MDM
3. Open APK → Install **NPTTE PharmaNG**
4. Set API: production builds embed `EXPO_PUBLIC_API_BASE_URL` from `eas.json` preview profile

## Field testing checklist

### Auth & session
- [ ] Staff login with regulator account
- [ ] Session refresh after backgrounding 30+ minutes
- [ ] Secure logout clears local queues

### Scanning
- [ ] Citizen verification (no login)
- [ ] Regulator inspection scan + offline queue
- [ ] Customs shipment scan
- [ ] Warehouse rapid scan mode

### Evidence
- [ ] Photo capture + GPS stamp
- [ ] Offline evidence queue → sync on reconnect

### Offline
- [ ] Airplane mode scan → queue → sync at `/sync-health`
- [ ] Failed sync retry with backoff

### Permissions
- [ ] Camera denied → clear message
- [ ] Location denied → scan still works without GPS
- [ ] Biometric enable in Settings

### Device trust
- [ ] Login registers device trust
- [ ] Heartbeat on login

## Regulator internal rollout

Distribute preview APK to NAFDAC field officers via secure MDM or signed download portal. Do not publish APK on public websites without organizational approval.

## Reporting issues

Capture: device model, Android version, `APP_ENV`, approximate time, screen, and whether offline mode was active.
