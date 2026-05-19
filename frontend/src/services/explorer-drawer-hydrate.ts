import { normalizeExplorerRecords } from "./explorer-format";
import {
  bundleCacheKey,
  getExplorerCacheStale,
  setExplorerCache,
  summaryCacheKey,
} from "./explorer-memory-cache";
import { fetchExplorerQuickBundle } from "./explorer";

export type QuickBundle = Record<string, unknown>;

export function readCachedQuickBundle(contextKey: string, page = 1): QuickBundle | null {
  return getExplorerCacheStale<QuickBundle>(bundleCacheKey(contextKey, page));
}

/** Apply bundle fields to drawer state setters. */
export function applyQuickBundleToState(
  bundle: QuickBundle,
  apply: {
    setOverview: (v: Record<string, unknown>) => void;
    setDetail: (v: Record<string, unknown>) => void;
    setActions: (v: { id: string; label: string; requires_confirm?: boolean; workflow?: string }[]) => void;
  }
) {
  const summaryText = bundle.summary;
  apply.setOverview({
    summary: {
      title: bundle.title,
      body: typeof summaryText === "string" ? summaryText : (summaryText as Record<string, unknown>)?.body,
    },
    record_count: bundle.count,
    record_preview: bundle.top_records,
    risk_status: bundle.status ?? bundle.risk_status,
    risk_score: bundle.risk_score,
    top_states: bundle.top_states,
    top_organisations: bundle.top_organisations,
    updated_at: bundle.updated_at,
  });
  const records = normalizeExplorerRecords(bundle.records ?? bundle.top_records);
  apply.setDetail({ records });
  const acts = bundle.actions;
  apply.setActions(Array.isArray(acts) ? (acts as { id: string; label: string; requires_confirm?: boolean; workflow?: string }[]) : []);
}

/** Fetch quick-bundle and update caches (stale-while-revalidate). */
export async function hydrateQuickBundle(contextKey: string, page = 1, pageSize = 25) {
  const res = await fetchExplorerQuickBundle(contextKey, page, pageSize);
  if (res.success && res.data) {
    const data = res.data;
    setExplorerCache(bundleCacheKey(contextKey, page), data);
    setExplorerCache(summaryCacheKey({ contextKey }), data);
  }
  return res;
}
