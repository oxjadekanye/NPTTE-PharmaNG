import { fetchExplorerQuickSummary } from "./explorer";
import { setExplorerCache, summaryCacheKey, getExplorerCache, TTL_SUMMARY_MS } from "./explorer-memory-cache";
import { enqueueHydration, HydrationPriority, cancelHydration } from "./hydration-queue";

const recent = new Map<string, number>();
const LRU_MAX = 40;
let lastHover = 0;
const HOVER_THROTTLE_MS = 400;

function touchLru(key: string) {
  recent.set(key, Date.now());
  if (recent.size > LRU_MAX) {
    const oldest = [...recent.entries()].sort((a, b) => a[1] - b[1])[0]?.[0];
    if (oldest) recent.delete(oldest);
  }
}

/** Prefetch quick-summary for a dashboard context (hover / repeat visit). */
export function prefetchContextOnHover(contextKey: string): void {
  if (!contextKey) return;
  const now = Date.now();
  if (now - lastHover < HOVER_THROTTLE_MS) return;
  lastHover = now;

  const cacheKey = summaryCacheKey({ contextKey });
  if (getExplorerCache(cacheKey, TTL_SUMMARY_MS)) {
    touchLru(contextKey);
    return;
  }

  const taskId = `prefetch:ctx:${contextKey}`;
  cancelHydration(taskId);
  enqueueHydration(
    taskId,
    async (signal) => {
      if (signal.aborted) return;
      const res = await fetchExplorerQuickSummary(contextKey, { lite: true });
      if (res.success && res.data) {
        setExplorerCache(cacheKey, res.data);
        touchLru(contextKey);
      }
    },
    HydrationPriority.HOVER
  );
}

/** Prefetch when user hovers nav link (route-level). */
export function prefetchRouteOnHover(href: string): void {
  if (!href.includes("command-center")) return;
  prefetchContextOnHover("national_status");
}
