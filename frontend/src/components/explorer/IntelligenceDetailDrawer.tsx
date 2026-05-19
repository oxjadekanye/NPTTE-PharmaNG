"use client";

import { memo, useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import clsx from "clsx";
import {
  fetchExplorerActions,
  fetchExplorerDetail,
  fetchExplorerEvidence,
  fetchExplorerOverview,
  fetchExplorerRelated,
  fetchExplorerRiskBreakdown,
  fetchExplorerTimeline,
} from "@/services/explorer";
import { useExplorerDrawerStore } from "@/store/explorer-drawer-store";
import { ExplorerActionModal, type ExplorerWorkflow } from "./ExplorerActionModal";
import { ExplorerCopilotPlaceholder } from "./ExplorerCopilotPlaceholder";
import { ExplorerDrawerSkeleton } from "./ExplorerDrawerSkeleton";
import { ExplorerEvidenceTable } from "./ExplorerEvidenceTable";
import { ExplorerRecordsTable } from "./ExplorerRecordsTable";
import { ExplorerRelatedCards } from "./ExplorerRelatedCards";
import { ExplorerRiskPanel } from "./ExplorerRiskPanel";
import { ExplorerSeverityBadge } from "./ExplorerSeverityBadge";
import { ExplorerTimelineList } from "./ExplorerTimelineList";

function explorerPageHref(entityType: string, entityId: string) {
  return `/regulator/explorer/${encodeURIComponent(entityType)}/${encodeURIComponent(entityId)}`;
}

function IntelligenceDetailDrawerInner() {
  const open = useExplorerDrawerStore((s) => s.open);
  const target = useExplorerDrawerStore((s) => s.target);
  const closeDrawer = useExplorerDrawerStore((s) => s.closeDrawer);

  const [overviewLoading, setOverviewLoading] = useState(false);
  const [sectionsLoading, setSectionsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [overview, setOverview] = useState<Record<string, unknown> | null>(null);
  const [detail, setDetail] = useState<Record<string, unknown> | null>(null);
  const [risk, setRisk] = useState<Record<string, unknown> | null>(null);
  const [timeline, setTimeline] = useState<Record<string, unknown>[]>([]);
  const [evidence, setEvidence] = useState<Record<string, unknown>[]>([]);
  const [related, setRelated] = useState<Record<string, unknown> | null>(null);
  const [actions, setActions] = useState<
    { id: string; label: string; requires_confirm?: boolean; workflow?: string }[]
  >([]);
  const [filter, setFilter] = useState("");
  const [execMsg, setExecMsg] = useState<string | null>(null);
  const [modal, setModal] = useState<{
    workflow: ExplorerWorkflow;
    actionId: string;
    label: string;
  } | null>(null);

  const entityType = target?.entityType ?? "";
  const entityId = target?.entityId ?? "";

  const load = useCallback(async () => {
    if (!target) return;
    setOverviewLoading(true);
    setSectionsLoading(true);
    setError(null);
    setExecMsg(null);
    setOverview(null);
    setDetail(null);

    try {
      const ovRes = await fetchExplorerOverview(target.entityType, target.entityId);
      if (ovRes.success && ovRes.data) {
        setOverview(ovRes.data as Record<string, unknown>);
      }
    } catch {
      /* overview optional */
    } finally {
      setOverviewLoading(false);
    }

    try {
      const [d, r, t, e, rel, a] = await Promise.all([
        fetchExplorerDetail(target.entityType, target.entityId),
        fetchExplorerRiskBreakdown(target.entityType, target.entityId).catch(() => null),
        fetchExplorerTimeline(target.entityType, target.entityId).catch(() => null),
        fetchExplorerEvidence(target.entityType, target.entityId).catch(() => null),
        fetchExplorerRelated(target.entityType, target.entityId).catch(() => null),
        fetchExplorerActions(target.entityType, target.entityId).catch(() => null),
      ]);
      if (!d.success) {
        setError(d.message || "Unable to load explorer detail");
        return;
      }
      setDetail((d.data as Record<string, unknown>) ?? null);
      setRisk(r?.success ? (r.data as Record<string, unknown>) : null);
      const tItems = (t?.data as { timeline?: { items?: unknown[] } })?.timeline;
      setTimeline((tItems?.items ?? (tItems as unknown as unknown[]) ?? []) as Record<string, unknown>[]);
      const eItems = (e?.data as { evidence?: { items?: unknown[] } })?.evidence;
      setEvidence((eItems?.items ?? (eItems as unknown as unknown[]) ?? []) as Record<string, unknown>[]);
      setRelated((rel?.data as { related_entities?: Record<string, unknown> })?.related_entities ?? null);
      setActions((a?.data as { actions?: typeof actions })?.actions ?? []);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setSectionsLoading(false);
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

  const summary = (detail?.summary as Record<string, unknown>) ?? (overview?.summary as Record<string, unknown>) ?? {};
  const severity = String(summary.severity ?? overview?.risk_status ?? "");
  const loading = overviewLoading && sectionsLoading;

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
          "flex h-full w-full max-w-lg flex-col border-l border-sovereign-800 bg-sovereign-950 shadow-2xl"
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
            <p className="mt-0.5 flex flex-wrap items-center gap-2 text-[10px] uppercase tracking-wider text-slate-500">
              <span>
                {entityType} · {entityId}
              </span>
              {severity && <ExplorerSeverityBadge severity={severity} />}
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
          {loading && <ExplorerDrawerSkeleton />}
          {error && (
            <div className="rounded-lg border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-200">
              <p>{error}</p>
              <button
                type="button"
                className="mt-2 text-xs text-sovereign-accent hover:underline"
                onClick={() => void load()}
              >
                Retry
              </button>
            </div>
          )}
          {!error && (overview || detail || overviewLoading) && (
            <div className="space-y-4 text-xs text-slate-300">
              {(detail || overview) && (
                <div className="flex flex-wrap gap-2 text-[10px] text-slate-500">
                  <span>Visibility: {String(detail?.tenant_visibility ?? overview?.tenant_visibility ?? "—")}</span>
                  {(detail?.confidence_score ?? overview?.confidence_score) != null && (
                    <span>Confidence: {String(detail?.confidence_score ?? overview?.confidence_score)}</span>
                  )}
                </div>
              )}
              {summary.body != null && String(summary.body).length > 0 && (
                <p className="text-sm text-slate-200">{String(summary.body)}</p>
              )}
              {sectionsLoading && !detail ? (
                <ExplorerDrawerSkeleton />
              ) : (
                <>
                  <ExplorerRiskPanel risk={risk} />
                  <ExplorerRecordsTable records={records} filter={filter} onFilterChange={setFilter} />
                  <section>
                    <h4 className="text-[11px] font-semibold uppercase text-slate-400">Timeline</h4>
                    <div className="mt-2">
                      <ExplorerTimelineList items={timeline} />
                    </div>
                  </section>
                  <section>
                    <h4 className="text-[11px] font-semibold uppercase text-slate-400">Evidence</h4>
                    <div className="mt-2">
                      <ExplorerEvidenceTable items={evidence} />
                    </div>
                  </section>
                  <section>
                    <h4 className="text-[11px] font-semibold uppercase text-slate-400">Related entities</h4>
                    <div className="mt-2">
                      <ExplorerRelatedCards related={related} />
                    </div>
                  </section>
                  {actions.length > 0 && (
                    <section>
                      <h4 className="text-[11px] font-semibold uppercase text-slate-400">Actions</h4>
                      <ul className="mt-2 space-y-2">
                        {actions.map((act) => (
                          <li key={act.id}>
                            <button
                              type="button"
                              className="w-full rounded border border-sovereign-700 px-2 py-1.5 text-left text-xs text-sovereign-accent hover:bg-sovereign-800"
                              onClick={() =>
                                setModal({
                                  workflow: (act.workflow as ExplorerWorkflow) || "task",
                                  actionId: act.id,
                                  label: act.label,
                                })
                              }
                            >
                              {act.label}
                            </button>
                          </li>
                        ))}
                      </ul>
                    </section>
                  )}
                  {execMsg && <p className="text-emerald-400">{execMsg}</p>}
                  <ExplorerCopilotPlaceholder />
                </>
              )}
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
      <ExplorerActionModal
        open={Boolean(modal)}
        workflow={modal?.workflow ?? null}
        entityType={entityType}
        entityId={entityId}
        actionId={modal?.actionId ?? ""}
        actionLabel={modal?.label ?? ""}
        onClose={() => setModal(null)}
        onSuccess={(m) => {
          setExecMsg(m);
          void load();
        }}
      />
    </div>
  );
}

export const IntelligenceDetailDrawer = memo(IntelligenceDetailDrawerInner);
