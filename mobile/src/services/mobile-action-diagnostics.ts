/** Operational action logs — visible in adb logcat during APK field testing. */
export type MobileAction =
  | "capture_photo_pressed"
  | "ai_recommendation_pressed"
  | "ai_inspection_recommendation_requested"
  | "inspection_tab_product_pressed"
  | "inspection_tab_compliance_pressed"
  | "alert_detail_opened"
  | "activity_detail_opened"
  | "retry_sync_all_pressed"
  | "retry_scan_sync_pressed";

export function mobileActionLog(action: MobileAction, detail?: string) {
  const suffix = detail ? ` — ${detail}` : "";
  // eslint-disable-next-line no-console
  console.log(`[MOBILE ACTION] ${action}${suffix}`);
}
