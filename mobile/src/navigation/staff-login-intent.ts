import { bootLog } from "@/services/boot-diagnostics";
import { useLandingIntent } from "@/store/landing-intent-store";
import { useNavigationStore } from "@/store/navigation-store";

export const STAFF_LOGIN_ROUTE = "/login";

export function landingLog(message: string) {
  // eslint-disable-next-line no-console
  console.log(`[LANDING] ${message}`);
}

/** Open staff login — survives AuthNavigationBridge when a session already exists. */
export function openStaffLogin() {
  landingLog("navigating_to_login");
  bootLog("navigation", "open staff login");
  useLandingIntent.getState().setPreferLanding(false);
  useLandingIntent.getState().setStaffLoginIntent(true);
  useNavigationStore.getState().clearNavigationDedupe();
  useNavigationStore.getState().pushStaffLoginWhenReady(STAFF_LOGIN_ROUTE);
}
