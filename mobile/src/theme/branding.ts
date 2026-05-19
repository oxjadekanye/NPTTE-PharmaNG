/**
 * NPTTE PharmaNG — sovereign production brand tokens (mobile).
 * Keep aligned with frontend/src/theme/branding.ts
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
    display: { fontSize: 32, lineHeight: 38, fontWeight: "800" as const },
    h1: { fontSize: 26, lineHeight: 32, fontWeight: "700" as const },
    h2: { fontSize: 22, lineHeight: 28, fontWeight: "700" as const },
    h3: { fontSize: 18, lineHeight: 24, fontWeight: "600" as const },
    body: { fontSize: 15, lineHeight: 22, fontWeight: "400" as const },
    caption: { fontSize: 12, lineHeight: 16, fontWeight: "500" as const },
    micro: { fontSize: 10, lineHeight: 14, fontWeight: "600" as const },
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 12,
    lg: 16,
    xl: 24,
    xxl: 32,
    section: 40,
  },
  icon: {
    sm: 16,
    md: 20,
    lg: 24,
    xl: 32,
  },
  radius: {
    sm: 8,
    md: 12,
    lg: 16,
    pill: 999,
  },
  shadow: {
    card: {
      shadowColor: "#000",
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.28,
      shadowRadius: 10,
      elevation: 6,
    },
    operational: {
      shadowColor: "#0284c7",
      shadowOffset: { width: 0, height: 6 },
      shadowOpacity: 0.32,
      shadowRadius: 14,
      elevation: 8,
    },
  },
} as const;

export type BrandColors = typeof NPTTEBrand.colors;
