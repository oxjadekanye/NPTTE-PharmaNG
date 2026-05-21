import { apiRequest } from "@/services/api-client";
import { cacheGet, cacheInvalidate, cacheSet } from "@/services/realtime/cache";
import { publishOperational } from "@/services/realtime/event-bus";

export type OperationalFeedPayload = {
  events: Array<Record<string, unknown>>;
  alerts: Array<Record<string, unknown>>;
  tasks: Array<Record<string, unknown>>;
  activity: Array<Record<string, unknown>>;
  since_sequence: number;
  polled_at: string;
};

const FEED_BATCH_LIMIT = 40;

export async function fetchOperationalFeed(params?: {
  since_sequence?: number;
  channels?: string;
  force?: boolean;
  limit?: number;
}) {
  const since = params?.since_sequence ?? 0;
  const cacheKey = `operational-feed:${since}:${params?.channels ?? "all"}`;
  if (!params?.force) {
    const cached = cacheGet<OperationalFeedPayload>(cacheKey);
    if (cached) return { success: true as const, data: cached, message: "cached" };
  }
  const q = new URLSearchParams();
  q.set("since_sequence", String(since));
  if (params?.channels) q.set("channels", params.channels);
  q.set("limit", String(params?.limit ?? FEED_BATCH_LIMIT));
  const res = await apiRequest<OperationalFeedPayload>(`/realtime/operational-feed/?${q}`);
  if (res.success && res.data) {
    cacheSet(cacheKey, res.data);
    res.data.events?.forEach((ev) => {
      const kind = String(ev.kind ?? "scan");
      publishOperational(kind as never, ev);
    });
  }
  return res;
}

export function invalidateOperationalFeed() {
  cacheInvalidate("operational-feed:");
}

export async function fetchPrefetchManifest() {
  return apiRequest<{
    routes: string[];
    poll_interval_ms: number;
    sse_url: string;
    feed_url: string;
  }>("/realtime/prefetch/");
}
