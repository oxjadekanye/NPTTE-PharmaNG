/** Operational action logs — visible in adb logcat during APK field testing. */
export type MobileAction =
  | "capture_photo_pressed"
  | "ai_recommendation_pressed"
  | "retry_sync_all_pressed"
  | "retry_scan_sync_pressed";

export function mobileActionLog(action: MobileAction, detail?: string) {
  const suffix = detail ? ` — ${detail}` : "";
  // eslint-disable-next-line no-console
  console.log(`[MOBILE ACTION] ${action}${suffix}`);
}
