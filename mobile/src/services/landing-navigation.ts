import { router } from "expo-router";
import { bootLog } from "@/services/boot-diagnostics";
import { useLandingIntent } from "@/store/landing-intent-store";
import { useNavigationStore } from "@/store/navigation-store";

export const STAFF_LOGIN_ROUTE = "/login";

/** Open staff login — survives AuthNavigationBridge when a session already exists. */
export function openStaffLogin() {
  bootLog("navigation", "open staff login");
  useLandingIntent.getState().setPreferLanding(false);
  useLandingIntent.getState().setStaffLoginIntent(true);
  useNavigationStore.getState().clearNavigationDedupe();
  useNavigationStore.getState().pushWhenReady(STAFF_LOGIN_ROUTE);
}
