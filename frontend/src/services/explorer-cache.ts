const PREFIX = "nptte_explorer_v20a4_";

type CacheEntry<T> = { ts: number; data: T };

export function readExplorerCache<T>(key: string, ttlMs: number): T | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = sessionStorage.getItem(PREFIX + key);
    if (!raw) return null;
    const entry = JSON.parse(raw) as CacheEntry<T>;
    if (Date.now() - entry.ts > ttlMs) return null;
    return entry.data;
  } catch {
    return null;
  }
}

export function writeExplorerCache<T>(key: string, data: T): void {
  if (typeof window === "undefined") return;
  try {
    const entry: CacheEntry<T> = { ts: Date.now(), data };
    sessionStorage.setItem(PREFIX + key, JSON.stringify(entry));
  } catch {
    /* quota */
  }
}

export function explorerCacheKey(parts: string[]): string {
  return parts.join(":");
}
