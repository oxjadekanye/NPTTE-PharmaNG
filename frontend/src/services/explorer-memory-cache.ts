// In-memory + sessionStorage cache with stale-while-revalidate for explorer.
import { readExplorerCache, writeExplorerCache, explorerCacheKey } from "./explorer-cache";

const memory = new Map<string, { ts: number; data: unknown }>();

export const TTL_SUMMARY_MS = 120_000;
export const TTL_RECORDS_MS = 120_000;
export const TTL_BUNDLE_MS = 120_000;
/** Show stale data while revalidating (up to 5 min). */
export const TTL_STALE_MS = 300_000;

function memKey(key: string) {
  return key;
}

export function getExplorerCache<T>(key: string, ttlMs: number): T | null {
  const mk = memKey(key);
  const hit = memory.get(mk);
  if (hit && Date.now() - hit.ts <= ttlMs) {
    return hit.data as T;
  }
  const session = readExplorerCache<T>(key, ttlMs);
  if (session) {
    memory.set(mk, { ts: Date.now(), data: session });
    return session;
  }
  return null;
}

/** Return cached payload even if slightly expired — for instant paint while refreshing. */
export function getExplorerCacheStale<T>(key: string, staleMs = TTL_STALE_MS): T | null {
  const mk = memKey(key);
  const hit = memory.get(mk);
  if (hit && Date.now() - hit.ts <= staleMs) {
    return hit.data as T;
  }
  const session = readExplorerCache<T>(key, staleMs);
  if (session) {
    memory.set(mk, { ts: Date.now(), data: session });
    return session;
  }
  return null;
}

export function setExplorerCache<T>(key: string, data: T): void {
  memory.set(memKey(key), { ts: Date.now(), data });
  writeExplorerCache(key, data);
}

export function summaryCacheKey(contextOrEntity: {
  contextKey?: string;
  entityType?: string;
  entityId?: string;
}) {
  if (contextOrEntity.contextKey) {
    return explorerCacheKey(["quick-summary", contextOrEntity.contextKey]);
  }
  return explorerCacheKey([
    "quick-summary",
    contextOrEntity.entityType ?? "",
    contextOrEntity.entityId ?? "",
  ]);
}

export function bundleCacheKey(contextKey: string, page = 1) {
  return explorerCacheKey(["quick-bundle", contextKey, String(page)]);
}

export function recordsCacheKey(contextKey: string, page = 1) {
  return explorerCacheKey(["quick-records", contextKey, String(page)]);
}
