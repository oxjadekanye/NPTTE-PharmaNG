import { router } from "expo-router";
import { bootLog } from "@/services/boot-diagnostics";
import { useLandingIntent } from "@/store/landing-intent-store";
import { useNavigationStore } from "@/store/navigation-store";

export const CITIZEN_ROUTES = {
  home: "/citizen",
  scan: "/citizen/scan",
  manual: "/citizen/manual",
  recalls: "/citizen/recalls",
  report: "/citizen/report",
} as const;

export type CitizenRoute = (typeof CITIZEN_ROUTES)[keyof typeof CITIZEN_ROUTES];

/** Imperative citizen navigation — avoids Link/asChild on Android APK. */
export function pushCitizenRoute(href: CitizenRoute) {
  bootLog("navigation", `citizen push → ${href}`);
  useNavigationStore.getState().clearNavigationDedupe();
  try {
    router.push(href as never);
  } catch (err) {
    bootLog("navigation", `citizen push failed ${err instanceof Error ? err.message : ""}`);
    router.replace(href as never);
  }
}

/** Return to production landing and allow public flow flags to reset. */
export function returnToLanding() {
  bootLog("navigation", "citizen → landing");
  useLandingIntent.getState().clearPublicFlow();
  useLandingIntent.getState().setPreferLanding(true);
  useNavigationStore.getState().clearNavigationDedupe();
  try {
    router.replace("/" as never);
  } catch {
    router.push("/" as never);
  }
}
