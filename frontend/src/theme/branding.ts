/**
 * NPTTE PharmaNG — sovereign production brand tokens (web).
 * Keep aligned with mobile/src/theme/branding.ts
 */
export const NPTTEBrand = {
  name: "NPTTE PharmaNG",
  tagline: "National Pharmaceutical Traceability & Enforcement Platform",
  colors: {
    sovereign: {
      bg: "#020617",
      surface: "#0f172a",
      elevated: "#1e293b",
      border: "#334155",
      text: "#f8fafc",
      muted: "#94a3b8",
      accent: "#38bdf8",
      accentStrong: "#0284c7",
    },
    alert: {
      info: "#38bdf8",
      success: "#22c55e",
      successMuted: "#86efac",
      warning: "#fbbf24",
      danger: "#ef4444",
      dangerSurface: "#7f1d1d",
    },
    enforcement: {
      primary: "#b45309",
      border: "#f59e0b",
      glow: "#fbbf24",
    },
    intelligence: {
      primary: "#6366f1",
      accent: "#a78bfa",
      glow: "#818cf8",
    },
    operational: {
      live: "#4ade80",
      liveBg: "#14532d",
      offline: "#f87171",
      pending: "#fcd34d",
    },
  },
  gradients: {
    command: ["#020617", "#0f172a", "#020617"] as const,
    operational: ["#0284c7", "#0369a1"] as const,
    enforcement: ["#7f1d1d", "#450a0a"] as const,
    intelligence: ["#312e81", "#1e1b4b"] as const,
  },
  typography: {
    display: { fontSize: "2rem", lineHeight: 1.2, fontWeight: 800 },
    h1: { fontSize: "1.625rem", lineHeight: 1.25, fontWeight: 700 },
    h2: { fontSize: "1.375rem", lineHeight: 1.3, fontWeight: 700 },
    h3: { fontSize: "1.125rem", lineHeight: 1.35, fontWeight: 600 },
    body: { fontSize: "0.9375rem", lineHeight: 1.5, fontWeight: 400 },
    caption: { fontSize: "0.75rem", lineHeight: 1.35, fontWeight: 500 },
    micro: { fontSize: "0.625rem", lineHeight: 1.4, fontWeight: 600 },
  },
  spacing: {
    xs: "0.25rem",
    sm: "0.5rem",
    md: "0.75rem",
    lg: "1rem",
    xl: "1.5rem",
    xxl: "2rem",
    section: "2.5rem",
  },
  icon: {
    sm: 16,
    md: 20,
    lg: 24,
    xl: 32,
  },
  radius: {
    sm: "0.5rem",
    md: "0.75rem",
    lg: "1rem",
    pill: "9999px",
  },
} as const;

/** CSS custom properties for globals.css */
export function brandingCssVariables(): Record<string, string> {
  const c = NPTTEBrand.colors.sovereign;
  return {
    "--nptte-bg": c.bg,
    "--nptte-surface": c.surface,
    "--nptte-elevated": c.elevated,
    "--nptte-border": c.border,
    "--nptte-text": c.text,
    "--nptte-muted": c.muted,
    "--nptte-accent": c.accent,
    "--nptte-accent-strong": c.accentStrong,
    "--nptte-success": NPTTEBrand.colors.alert.success,
    "--nptte-warning": NPTTEBrand.colors.alert.warning,
    "--nptte-danger": NPTTEBrand.colors.alert.danger,
    "--nptte-enforcement": NPTTEBrand.colors.enforcement.primary,
    "--nptte-intelligence": NPTTEBrand.colors.intelligence.primary,
  };
}
