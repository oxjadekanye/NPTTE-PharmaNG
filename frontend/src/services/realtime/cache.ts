/** Phase 11 — simple TTL cache for polling feeds. */

type Entry<T> = { data: T; expires: number };

const store = new Map<string, Entry<unknown>>();

export function cacheGet<T>(key: string): T | null {
  const hit = store.get(key);
  if (!hit) return null;
  if (Date.now() > hit.expires) {
    store.delete(key);
    return null;
  }
  return hit.data as T;
}

export function cacheSet<T>(key: string, data: T, ttlMs = 15000) {
  store.set(key, { data, expires: Date.now() + ttlMs });
}

export function cacheInvalidate(prefix?: string) {
  if (!prefix) {
    store.clear();
    return;
  }
  for (const k of store.keys()) {
    if (k.startsWith(prefix)) store.delete(k);
  }
}
