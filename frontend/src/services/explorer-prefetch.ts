import { fetchExplorerQuickSummary } from "./explorer";
import { writeExplorerCache, explorerCacheKey } from "./explorer-cache";
import { HOT_PREFETCH_CONTEXTS } from "./explorer-context-map";
import { enqueueHydration, HydrationPriority } from "./hydration-queue";

let prefetchStarted = false;

/** Background warm of hot dashboard contexts (stale-while-revalidate). */
export function prefetchHotExplorerContexts(): void {
  if (typeof window === "undefined" || prefetchStarted) return;
  prefetchStarted = true;
  const run = () => {
    for (const ctx of HOT_PREFETCH_CONTEXTS) {
      enqueueHydration(
        `prefetch:hot:${ctx}`,
        async (signal) => {
          if (signal.aborted) return;
          const res = await fetchExplorerQuickSummary(ctx, { lite: true });
          if (res.success && res.data) {
            writeExplorerCache(explorerCacheKey(["quick-summary", ctx]), res.data);
          }
        },
        HydrationPriority.PREFETCH
      );
    }
  };
  if ("requestIdleCallback" in window) {
    (window as Window & { requestIdleCallback: (cb: () => void) => void }).requestIdleCallback(run);
  } else {
    setTimeout(run, 800);
  }
}
