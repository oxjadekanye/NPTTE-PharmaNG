import { fetchExplorerQuickSummary } from "./explorer";
import { writeExplorerCache, explorerCacheKey } from "./explorer-cache";
import { HOT_PREFETCH_CONTEXTS, resolveContextTarget } from "./explorer-context-map";

let prefetchStarted = false;

/** Background warm of hot dashboard contexts (stale-while-revalidate). */
export function prefetchHotExplorerContexts(): void {
  if (typeof window === "undefined" || prefetchStarted) return;
  prefetchStarted = true;
  const run = () => {
    for (const ctx of HOT_PREFETCH_CONTEXTS) {
      void fetchExplorerQuickSummary(ctx).then((res) => {
        if (res.success && res.data) {
          writeExplorerCache(explorerCacheKey(["quick-summary", ctx]), res.data);
        }
      });
    }
  };
  if ("requestIdleCallback" in window) {
    (window as Window & { requestIdleCallback: (cb: () => void) => void }).requestIdleCallback(run);
  } else {
    setTimeout(run, 800);
  }
}
