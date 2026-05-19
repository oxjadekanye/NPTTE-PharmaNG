import { apiRequest } from "@/services/api-client";

export type MobileFeedEvent = {
  event_id?: string;
  event_type?: string;
  payload?: Record<string, unknown>;
  sequence_number?: number;
};

export async function fetchMobileRealtimeFeed(channel: string, sinceSequence = 0) {
  return apiRequest<{ events: MobileFeedEvent[]; channel: string }>(
    `/mobile/realtime/feed/?channel=${encodeURIComponent(channel)}&since_sequence=${sinceSequence}`
  );
}
