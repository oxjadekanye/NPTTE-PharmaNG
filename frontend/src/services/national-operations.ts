import { apiRequest } from "./api-client";

export type NationalOperationsSummary = {
  national_threat_index: number;
  verifications_24h_roll: number;
  active_recalls: number;
  customs_holds_open: number;
  warehouse_inspections_scheduled: number;
  shortage_watch_states: string[];
  recent_event_sample: unknown[];
  generated_at: string;
  note?: string;
};

export async function fetchNationalOperationsSummary() {
  return apiRequest<NationalOperationsSummary>("/events/national-summary/", { method: "GET" });
}
