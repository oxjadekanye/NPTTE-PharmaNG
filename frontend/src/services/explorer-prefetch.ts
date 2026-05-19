import {
  fetchExplorerContextSummary,
  fetchExplorerOverview,
} from "./explorer";
import { writeExplorerCache, explorerCacheKey } from "./explorer-cache";
import { HOT_PREFETCH_CONTEXTS, resolveContextTarget } from "./explorer-context-map";

let prefetchStarted = false;

/** Background warm of hot dashboard contexts (stale-while-revalidate). */
export function prefetchHotExplorerContexts(): void {
  if (typeof window === "undefined" || prefetchStarted) return;
  prefetchStarted = true;
  const run = () => {
    for (const ctx of HOT_PREFETCH_CONTEXTS) {
      void fetchExplorerContextSummary(ctx).then((res) => {
        if (res.success && res.data) {
          writeExplorerCache(explorerCacheKey(["summary", ctx]), res.data);
          const route = res.data.route as { entity_type?: string; entity_id?: string } | undefined;
          const hint = resolveContextTarget(ctx);
          const et = route?.entity_type ?? hint.entityType;
          const eid = route?.entity_id ?? hint.entityId;
          void fetchExplorerOverview(et, eid).then((ov) => {
            if (ov.success && ov.data) {
              writeExplorerCache(explorerCacheKey(["overview", et, eid]), ov.data);
            }
          });
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
