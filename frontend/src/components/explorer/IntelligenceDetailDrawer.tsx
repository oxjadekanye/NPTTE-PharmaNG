"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import clsx from "clsx";
import {
  executeExplorerAction,
  fetchExplorerActions,
  fetchExplorerDetail,
  fetchExplorerEvidence,
  fetchExplorerRiskBreakdown,
  fetchExplorerTimeline,
} from "@/services/explorer";
import { useExplorerDrawerStore } from "@/store/explorer-drawer-store";

function explorerPageHref(entityType: string, entityId: string) {
  return `/regulator/explorer/${encodeURIComponent(entityType)}/${encodeURIComponent(entityId)}`;
}

export function IntelligenceDetailDrawer() {
  const open = useExplorerDrawerStore((s) => s.open);
  const target = useExplorerDrawerStore((s) => s.target);
  const closeDrawer = useExplorerDrawerStore((s) => s.closeDrawer);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [detail, setDetail] = useState<Record<string, unknown> | null>(null);
  const [risk, setRisk] = useState<Record<string, unknown> | null>(null);
  const [timeline, setTimeline] = useState<unknown[]>([]);
  const [evidence, setEvidence] = useState<unknown[]>([]);
  const [actions, setActions] = useState<{ id: string; label: string; requires_confirm?: boolean }[]>([]);
  const [filter, setFilter] = useState("");
  const [execMsg, setExecMsg] = useState<string | null>(null);

  const entityType = target?.entityType ?? "";
  const entityId = target?.entityId ?? "";

  const load = useCallback(async () => {
    if (!target) return;
    setLoading(true);
    setError(null);
    setExecMsg(null);
    try {
      const [d, r, t, e, a] = await Promise.all([
        fetchExplorerDetail(target.entityType, target.entityId),
        fetchExplorerRiskBreakdown(target.entityType, target.entityId).catch(() => null),
        fetchExplorerTimeline(target.entityType, target.entityId).catch(() => null),
        fetchExplorerEvidence(target.entityType, target.entityId).catch(() => null),
        fetchExplorerActions(target.entityType, target.entityId).catch(() => null),
      ]);
      if (!d.success) {
        setError(d.message || "Unable to load explorer detail");
        setDetail(null);
        return;
      }
      setDetail((d.data as Record<string, unknown>) ?? null);
      setRisk(r?.success ? (r.data as Record<string, unknown>) : null);
      setTimeline((t?.data as { timeline?: unknown[] })?.timeline ?? []);
      setEvidence((e?.data as { evidence?: unknown[] })?.evidence ?? []);
      setActions((a?.data as { actions?: typeof actions })?.actions ?? []);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Request failed");
      setDetail(null);
    } finally {
      setLoading(false);
    }
  }, [target]);

  useEffect(() => {
    if (open && target) void load();
  }, [open, target, load]);

  const records = useMemo(() => {
    const raw = (detail?.records as Record<string, unknown>[]) ?? [];
    if (!filter.trim()) return raw;
    const q = filter.toLowerCase();
    return raw.filter((row) => JSON.stringify(row).toLowerCase().includes(q));
  }, [detail, filter]);

  if (!open || !target) return null;

  const summary = (detail?.summary as Record<string, unknown>) ?? {};

  return (
    <div className="fixed inset-0 z-[100] flex justify-end bg-black/50 backdrop-blur-sm" role="presentation">
      <button
        type="button"
        className="h-full flex-1 cursor-default border-0 bg-transparent"
        aria-label="Close drawer backdrop"
        onClick={closeDrawer}
      />
      <aside
        className={clsx(
          "flex h-full w-full max-w-lg flex-col border-l border-sovereign-800 bg-sovereign-950 shadow-2xl transition-transform duration-200"
        )}
        role="dialog"
        aria-modal="true"
        aria-labelledby="explorer-drawer-title"
      >
        <div className="flex items-start justify-between border-b border-sovereign-800 px-4 py-3">
          <div>
            <p id="explorer-drawer-title" className="text-sm font-semibold text-white">
              {String(summary.title ?? target.title ?? "Operational intelligence")}
            </p>
            <p className="mt-0.5 text-[10px] uppercase tracking-wider text-slate-500">
              {entityType} · {entityId}
            </p>
          </div>
          <button
            type="button"
            onClick={closeDrawer}
            className="rounded-lg border border-sovereign-700 px-2 py-1 text-xs text-slate-300 hover:bg-sovereign-800"
          >
            Close
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-4 py-3">
          {loading && <p className="text-sm text-slate-500">Loading operational picture…</p>}
          {error && (
            <div className="rounded-lg border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-200">
              <p>{error}</p>
              <button type="button" className="mt-2 text-xs text-sovereign-accent hover:underline" onClick={() => void load()}>
                Retry
              </button>
            </div>
          )}
          {!loading && !error && detail && (
            <div className="space-y-4 text-xs text-slate-300">
              <div className="flex flex-wrap gap-2 text-[10px] text-slate-500">
                <span>Visibility: {String(detail.tenant_visibility)}</span>
                {detail.confidence_score != null && <span>Confidence: {String(detail.confidence_score)}</span>}
              </div>
              {summary.body != null && String(summary.body).length > 0 && (
                <p className="text-sm text-slate-200">{String(summary.body)}</p>
              )}
              {risk && Object.keys(risk).length > 0 && (
                <section>
                  <h4 className="text-[11px] font-semibold uppercase text-slate-400">Risk breakdown</h4>
                  <pre className="mt-1 max-h-40 overflow-auto rounded border border-sovereign-800 bg-sovereign-900/80 p-2 text-[10px]">
                    {JSON.stringify(risk, null, 2)}
                  </pre>
                </section>
              )}
              <section>
                <h4 className="text-[11px] font-semibold uppercase text-slate-400">Records</h4>
                <input
                  type="search"
                  placeholder="Filter records…"
                  value={filter}
                  onChange={(ev) => setFilter(ev.target.value)}
                  className="mt-1 w-full rounded border border-sovereign-700 bg-sovereign-900 px-2 py-1 text-xs text-white"
                />
                <pre className="mt-2 max-h-48 overflow-auto rounded border border-sovereign-800 bg-sovereign-900/80 p-2 text-[10px]">
                  {JSON.stringify(records.slice(0, 40), null, 2)}
                </pre>
              </section>
              {timeline.length > 0 && (
                <section>
                  <h4 className="text-[11px] font-semibold uppercase text-slate-400">Timeline</h4>
                  <pre className="mt-1 max-h-32 overflow-auto rounded border border-sovereign-800 bg-sovereign-900/80 p-2 text-[10px]">
                    {JSON.stringify(timeline.slice(0, 20), null, 2)}
                  </pre>
                </section>
              )}
              {evidence.length > 0 && (
                <section>
                  <h4 className="text-[11px] font-semibold uppercase text-slate-400">Evidence</h4>
                  <pre className="mt-1 max-h-32 overflow-auto rounded border border-sovereign-800 bg-sovereign-900/80 p-2 text-[10px]">
                    {JSON.stringify(evidence, null, 2)}
                  </pre>
                </section>
              )}
              {actions.length > 0 && (
                <section>
                  <h4 className="text-[11px] font-semibold uppercase text-slate-400">Actions</h4>
                  <ul className="mt-2 space-y-2">
                    {actions.map((act) => (
                      <li key={act.id}>
                        <button
                          type="button"
                          className="w-full rounded border border-sovereign-700 px-2 py-1.5 text-left text-xs text-sovereign-accent hover:bg-sovereign-800"
                          onClick={async () => {
                            setExecMsg(null);
                            try {
                              const res = await executeExplorerAction(entityType, entityId, {
                                action_id: act.id,
                                confirm: act.requires_confirm ? true : false,
                                title: `Explorer: ${act.label}`,
                              });
                              if (res.success) setExecMsg("Action completed.");
                              else setExecMsg(res.message || "Action failed");
                            } catch {
                              setExecMsg("Action failed (regulator-only or confirmation required).");
                            }
                          }}
                        >
                          {act.label}
                          {act.requires_confirm ? " (confirms)" : ""}
                        </button>
                      </li>
                    ))}
                  </ul>
                </section>
              )}
              {execMsg && <p className="text-emerald-400">{execMsg}</p>}
              <section className="rounded border border-dashed border-sovereign-700 p-2 text-[10px] text-slate-500">
                Phase 20 — Copilot / LLM assist placeholder (no external calls in this phase).
              </section>
            </div>
          )}
        </div>

        <div className="border-t border-sovereign-800 px-4 py-3">
          <Link
            href={explorerPageHref(entityType, entityId)}
            className="text-sm text-sovereign-accent hover:underline"
            onClick={closeDrawer}
          >
            Open full detail page →
          </Link>
        </div>
      </aside>
    </div>
  );
}
