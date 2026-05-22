import { Platform, StyleSheet } from "react-native";

export const LANDING_CTA_MIN_HEIGHT = 86;

export const LANDING_COLORS = {
  bg: "#020617",
  bgMid: "#0a1628",
  grid: "#1e3a5f66",
  gridBright: "#38bdf822",
  text: "#FFFFFF",
  subtitle: "#cbd5e1",
  badgeGreen: "#4ade80",
  badgeBorder: "#22c55e88",
  badgeBg: "#14532d66",
} as const;

export type LandingCtaVariant = "primary" | "staff" | "accent" | "alert";

export const LANDING_CTA_VARIANTS: Record<
  LandingCtaVariant,
  {
    fill: string;
    fillHighlight: string;
    border: string;
    glow: string;
    icon: string;
  }
> = {
  primary: {
    fill: "#0c4a9e",
    fillHighlight: "rgba(34, 211, 238, 0.18)",
    border: "#22d3ee",
    glow: "#38bdf8",
    icon: "✦",
  },
  staff: {
    fill: "#0b3d6e",
    fillHighlight: "rgba(125, 211, 252, 0.14)",
    border: "#7dd3fc",
    glow: "#0ea5e9",
    icon: "⬡",
  },
  accent: {
    fill: "#312e81",
    fillHighlight: "rgba(167, 139, 250, 0.2)",
    border: "#a78bfa",
    glow: "#818cf8",
    icon: "⚠",
  },
  alert: {
    fill: "#9f1239",
    fillHighlight: "rgba(251, 146, 60, 0.22)",
    border: "#fb923c",
    glow: "#ef4444",
    icon: "!",
  },
};

export const landingShared = StyleSheet.create({
  ctaLabel: {
    flex: 1,
    color: LANDING_COLORS.text,
    fontSize: 21,
    fontWeight: "800",
    letterSpacing: 0.3,
    textAlign: "left",
  },
  ctaIconWrap: {
    width: 44,
    height: 44,
    borderRadius: 12,
    backgroundColor: "rgba(255, 255, 255, 0.12)",
    alignItems: "center",
    justifyContent: "center",
    marginRight: 14,
    borderWidth: 1,
    borderColor: "rgba(255, 255, 255, 0.2)",
  },
  ctaIcon: {
    color: LANDING_COLORS.text,
    fontSize: 22,
    fontWeight: "800",
  },
  ctaRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "flex-start",
    width: "100%",
    paddingHorizontal: 18,
  },
  ctaHighlight: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    height: "42%",
    borderTopLeftRadius: 14,
    borderTopRightRadius: 14,
  },
  ctaGlowRing: {
    position: "absolute",
    top: -3,
    left: -3,
    right: -3,
    bottom: -3,
    borderRadius: 17,
    borderWidth: 2,
  },
});

export function ctaShadow(glow: string) {
  return Platform.select({
    android: { elevation: 14 },
    ios: {
      shadowColor: glow,
      shadowOffset: { width: 0, height: 8 },
      shadowOpacity: 0.65,
      shadowRadius: 18,
    },
    default: { elevation: 14 },
  });
}
