# NPTTE PharmaNG — Brand Assets

Canonical branding assets for mobile, web, and release pipelines.

## Structure

| Asset | Path | Usage |
|-------|------|--------|
| App icon | `icon.png` (1024×1024) | iOS/Android store |
| Adaptive foreground | `adaptive-icon-foreground.png` (432×432) | Android adaptive icon safe zone |
| Splash logo | `splash-logo.png` (1024×1024) | Expo native splash + in-app boot |
| Notification icon | `notification-icon.png` (96×96, white glyph) | Android notifications |
| Favicon | `favicon.png` / `favicon.svg` | Web |
| Executive emblem | `executive-emblem.svg` | Executive dashboards |
| Source vectors | `*.svg` | Design exports |

Mobile build copies reference `mobile/assets/branding/` (sync from this folder before release).

## Dark mode

- Use transparent SVG logos on `#020617` sovereign background
- Android adaptive icon background: `#020617`

## Replacing placeholders

Current PNGs are solid-color placeholders for EAS builds. Replace with final NAFDAC/NPTTE artwork:

```bash
# After design export
cp design/icon-1024.png mobile/assets/branding/icon.png
cp design/adaptive-432.png mobile/assets/branding/adaptive-icon-foreground.png
```

## Safe zone (Android adaptive)

Keep logo glyph within center **66%** circle of foreground image.
