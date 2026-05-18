import { apiRequest } from "./api-client";

export async function fetchCustodyTimeline(serial_number: string) {
  return apiRequest<{ timeline: unknown[]; serial_number: string }>(
    `/traceability/custody/timeline/?serial_number=${encodeURIComponent(serial_number)}`
  );
}

export async function fetchRecallExecutionCampaigns() {
  return apiRequest<{ campaigns: unknown[] }>("/traceability/recall-execution/");
}
