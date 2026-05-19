import { apiRequest } from "@/services/api-client";

export async function fetchMobileAuditTimeline() {
  return apiRequest<{ timeline: Record<string, unknown>[] }>("/mobile/audit/timeline/");
}

/** Client-side audit marker — authoritative trail is on server scan/evidence APIs. */
export function recordMobileAudit(actionType: string, payload: Record<string, unknown> = {}) {
  if (typeof __DEV__ !== "undefined" && __DEV__) {
    // eslint-disable-next-line no-console
    console.log("[mobile-audit]", actionType, payload);
  }
  return Promise.resolve({ success: true as const });
}
