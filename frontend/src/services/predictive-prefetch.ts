import { prefetchExplorerContext } from "./explorer-routing";

const recent = new Map<string, number>();
const LRU_MAX = 40;
let lastHover = 0;
const HOVER_THROTTLE_MS = 300;

function touchLru(key: string) {
  recent.set(key, Date.now());
  if (recent.size > LRU_MAX) {
    const oldest = [...recent.entries()].sort((a, b) => a[1] - b[1])[0]?.[0];
    if (oldest) recent.delete(oldest);
  }
}

/** Prefetch full quick-bundle for a dashboard context (hover / repeat visit). */
export function prefetchContextOnHover(contextKey: string): void {
  if (!contextKey) return;
  const now = Date.now();
  if (now - lastHover < HOVER_THROTTLE_MS) return;
  lastHover = now;
  touchLru(contextKey);
  prefetchExplorerContext(contextKey);
}

/** Prefetch when user hovers nav link (route-level). */
export function prefetchRouteOnHover(href: string): void {
  if (href === "/regulator" || href.endsWith("/regulator")) {
    prefetchContextOnHover("national_status");
    return;
  }
  if (href.includes("command-center")) {
    prefetchContextOnHover("national_status");
  }
}
