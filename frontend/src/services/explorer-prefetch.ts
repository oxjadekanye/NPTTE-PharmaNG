import { HOT_PREFETCH_CONTEXTS } from "./explorer-context-map";
import { prefetchExplorerContext } from "./explorer-routing";
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
          prefetchExplorerContext(ctx);
        },
        HydrationPriority.PREFETCH
      );
    }
  };
  if ("requestIdleCallback" in window) {
    (window as Window & { requestIdleCallback: (cb: () => void) => void }).requestIdleCallback(run);
  } else {
    setTimeout(run, 400);
  }
}
