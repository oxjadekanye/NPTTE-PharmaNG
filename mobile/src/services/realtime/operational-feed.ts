import { apiRequest } from "@/services/api-client";

export type MobileOperationalFeed = {
  events: Array<Record<string, unknown>>;
  alerts: Array<Record<string, unknown>>;
  tasks: Array<Record<string, unknown>>;
  activity: Array<Record<string, unknown>>;
  since_sequence: number;
  polled_at: string;
};

let lastSequence = 0;

export async function fetchOperationalFeedMobile(channels?: string) {
  const q = new URLSearchParams();
  q.set("since_sequence", String(lastSequence));
  if (channels) q.set("channels", channels);
  const res = await apiRequest<MobileOperationalFeed>(`/realtime/operational-feed/?${q}`);
  if (res.success && res.data?.since_sequence) {
    lastSequence = res.data.since_sequence;
  }
  return res;
}

export function resetOperationalFeedSequence() {
  lastSequence = 0;
}
