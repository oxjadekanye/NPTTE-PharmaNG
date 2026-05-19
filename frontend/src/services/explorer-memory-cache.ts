// In-memory + sessionStorage cache with stale-while-revalidate for explorer.
import { readExplorerCache, writeExplorerCache, explorerCacheKey } from "./explorer-cache";

const memory = new Map<string, { ts: number; data: unknown }>();

export const TTL_SUMMARY_MS = 90_000;
export const TTL_RECORDS_MS = 60_000;

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

export function recordsCacheKey(contextKey: string, page = 1) {
  return explorerCacheKey(["quick-records", contextKey, String(page)]);
}
