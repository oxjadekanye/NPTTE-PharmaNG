"use client";

import { memo, useCallback, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import clsx from "clsx";
import {
  fetchExplorerActions,
  fetchExplorerDetail,
  fetchExplorerEvidence,
  fetchExplorerOverviewCached,
  fetchExplorerQuickActions,
  fetchExplorerQuickRecords,
  fetchExplorerQuickSummary,
  fetchExplorerRelated,
  fetchExplorerRiskBreakdown,
  fetchExplorerTimeline,
} from "@/services/explorer";
import {
  getExplorerCache,
  recordsCacheKey,
  setExplorerCache,
  summaryCacheKey,
  TTL_SUMMARY_MS,
} from "@/services/explorer-memory-cache";
import { normalizeExplorerRecords, recordSearchText, type OperationalRecord } from "@/services/explorer-format";
import { explorerFullPageHref } from "@/services/explorer-navigation";
import { openExplorerFromRecord } from "@/services/explorer-routing";
import { perfMark, perfMeasure } from "@/services/perf";
import { useExplorerDrawerStore } from "@/store/explorer-drawer-store";
import { ExplorerActionModal, type ExplorerWorkflow } from "./ExplorerActionModal";
import { ExplorerCopilotPlaceholder } from "./ExplorerCopilotPlaceholder";
import { ExplorerDrawerSkeleton } from "./ExplorerDrawerSkeleton";
import { ExplorerSeverityBadge } from "./ExplorerSeverityBadge";
import { ExplorerActionSummary } from "./renderers/ExplorerActionSummary";
import { ExplorerEvidencePanel } from "./renderers/ExplorerEvidencePanel";
import { ExplorerOperationalSummary } from "./renderers/ExplorerOperationalSummary";
import { ExplorerRecordsTable } from "./renderers/ExplorerRecordsTable";
import { ExplorerRiskFactors } from "./renderers/ExplorerRiskFactors";
import { ExplorerTimelineCard } from "./renderers/ExplorerTimelineCard";
import { ExplorerRelatedCards } from "./ExplorerRelatedCards";

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

  const abortRef = useRef<AbortController | null>(null);
  const [slowLoad, setSlowLoad] = useState(false);
  const [showRetry, setShowRetry] = useState(false);

  const applyQuickSummary = useCallback((s: Record<string, unknown>) => {
    setOverview({
      summary: {
        title: s.title,
        body: typeof s.summary === "string" ? s.summary : (s.summary as Record<string, unknown>)?.body,
      },
      record_count: s.count,
      record_preview: (s.top_records as Record<string, unknown>[]) ?? [],
      risk_status: s.status ?? s.risk_status,
      risk_score: s.risk_score,
      top_states: s.top_states,
      top_organisations: s.top_organisations,
      updated_at: s.updated_at,
    });
    setOverviewLoading(false);
  }, []);

  const entityType = target?.entityType ?? "";
  const entityId = target?.entityId ?? "";
  const displayTitle = String(
    target?.title ??
      (overview?.summary as Record<string, unknown> | undefined)?.title ??
      "Operational intelligence"
  );

  const load = useCallback(async () => {
    if (!target) return;
    abortRef.current?.abort();
    const ac = new AbortController();
    abortRef.current = ac;

    setOverviewLoading(true);
    setSectionsLoading(true);
    setError(null);
    setExecMsg(null);
    const cached =
      target.cachedSummary ??
      (target.contextKey
        ? getExplorerCache<Record<string, unknown>>(
            summaryCacheKey({ contextKey: target.contextKey }),
            TTL_SUMMARY_MS
          )
        : null);
    if (cached) applyQuickSummary(cached);
    else {
      setOverview(null);
      setDetail(null);
    }
    setRisk(null);
    setTimeline([]);
    setEvidence([]);
    setRelated(null);
    setActions([]);

    const { entityType: et, entityId: eid, contextKey } = target;

    try {
      if (contextKey) {
        const [sumRes, recRes, actRes] = await Promise.allSettled([
          fetchExplorerQuickSummary(contextKey),
          fetchExplorerQuickRecords(contextKey, 1, 25),
          fetchExplorerQuickActions(contextKey),
        ]);
        if (ac.signal.aborted) return;

        if (sumRes.status === "fulfilled" && sumRes.value.success && sumRes.value.data) {
          const s = sumRes.value.data;
          setExplorerCache(summaryCacheKey({ contextKey }), s);
          applyQuickSummary(s);
        }
        if (recRes.status === "fulfilled" && recRes.value.success && recRes.value.data) {
          const rec = recRes.value.data.records;
          setExplorerCache(recordsCacheKey(contextKey, 1), recRes.value.data);
          setDetail({ records: normalizeExplorerRecords(rec) });
        } else if (cached && (cached.top_records as unknown[])?.length) {
          setDetail({ records: normalizeExplorerRecords(cached.top_records) });
        }
        if (actRes.status === "fulfilled" && actRes.value.success) {
          setActions((actRes.value.data as { actions?: typeof actions })?.actions ?? []);
        }

        setOverviewLoading(false);
        setSectionsLoading(false);

        void Promise.allSettled([
          fetchExplorerRiskBreakdown(et, eid),
          fetchExplorerTimeline(et, eid, 1),
          fetchExplorerEvidence(et, eid, 1),
          fetchExplorerRelated(et, eid),
        ]).then(([r, t, e, rel]) => {
          if (ac.signal.aborted) return;
          if (r.status === "fulfilled" && r.value.success) setRisk(r.value.data as Record<string, unknown>);
          if (t.status === "fulfilled" && t.value.success) {
            const tItems = (t.value.data as { timeline?: { items?: unknown[] } })?.timeline;
            setTimeline((tItems?.items ?? []) as Record<string, unknown>[]);
          }
          if (e.status === "fulfilled" && e.value.success) {
            const eItems = (e.value.data as { evidence?: { items?: unknown[] } })?.evidence;
            setEvidence((eItems?.items ?? []) as Record<string, unknown>[]);
          }
          if (rel.status === "fulfilled" && rel.value.success) {
            setRelated(
              (rel.value.data as { related_entities?: Record<string, unknown> })?.related_entities ?? null
            );
          }
        });
      } else {
        const [ovRes, dRes, actRes, rRes] = await Promise.allSettled([
          fetchExplorerOverviewCached(et, eid),
          fetchExplorerDetail(et, eid, 1, 25),
          fetchExplorerActions(et, eid),
          fetchExplorerRiskBreakdown(et, eid),
        ]);
        if (ac.signal.aborted) return;

        if (ovRes.status === "fulfilled" && ovRes.value.success && ovRes.value.data) {
          setOverview(ovRes.value.data as Record<string, unknown>);
        }
        setOverviewLoading(false);

        if (dRes.status === "fulfilled") {
          if (!dRes.value.success) {
            setError(dRes.value.message || "Unable to load explorer detail");
          } else {
            const data = (dRes.value.data as Record<string, unknown>) ?? {};
            setDetail({
              ...data,
              records: normalizeExplorerRecords(data.records),
            });
          }
        }
        if (actRes.status === "fulfilled" && actRes.value.success) {
          setActions((actRes.value.data as { actions?: typeof actions })?.actions ?? []);
        }
        if (rRes.status === "fulfilled" && rRes.value.success) {
          setRisk(rRes.value.data as Record<string, unknown>);
        }

        setOverviewLoading(false);
        setSectionsLoading(false);

        const loadSecondary = et !== "notification";
        if (loadSecondary) {
          void Promise.allSettled([
            fetchExplorerTimeline(et, eid, 1),
            fetchExplorerEvidence(et, eid, 1),
            fetchExplorerRelated(et, eid),
          ]).then(([t, e, rel]) => {
            if (ac.signal.aborted) return;
            if (t.status === "fulfilled" && t.value.success) {
              const tItems = (t.value.data as { timeline?: { items?: unknown[] } })?.timeline;
              setTimeline((tItems?.items ?? []) as Record<string, unknown>[]);
            }
            if (e.status === "fulfilled" && e.value.success) {
              const eItems = (e.value.data as { evidence?: { items?: unknown[] } })?.evidence;
              setEvidence((eItems?.items ?? []) as Record<string, unknown>[]);
            }
            if (rel.status === "fulfilled" && rel.value.success) {
              setRelated(
                (rel.value.data as { related_entities?: Record<string, unknown> })?.related_entities ?? null
              );
            }
          });
        }
      }
      perfMeasure("explorer-drawer-content", "explorer-drawer-open");
    } catch (err: unknown) {
      if (!ac.signal.aborted) {
        setError(err instanceof Error ? err.message : "Request failed");
      }
    } finally {
      if (!ac.signal.aborted) {
        setOverviewLoading(false);
        setSectionsLoading(false);
      }
    }
  }, [target, applyQuickSummary]);

  useEffect(() => {
    if (open && target) {
      perfMark("explorer-drawer-open");
      setSlowLoad(false);
      setShowRetry(false);
      const tSlow = window.setTimeout(() => setSlowLoad(true), 800);
      const tRetry = window.setTimeout(() => setShowRetry(true), 8000);
      void load();
      return () => {
        clearTimeout(tSlow);
        clearTimeout(tRetry);
        abortRef.current?.abort();
      };
    }
    return () => abortRef.current?.abort();
  }, [open, target, load]);

  const openDrawer = useExplorerDrawerStore((s) => s.openDrawer);

  const records = useMemo(() => {
    const raw = normalizeExplorerRecords(detail?.records);
    const fromPreview = normalizeExplorerRecords(overview?.record_preview);
    const list = raw.length ? raw : fromPreview;
    if (!filter.trim()) return list;
    const q = filter.toLowerCase();
    return list.filter((row) => recordSearchText(row).includes(q));
  }, [detail, overview, filter]);

  const onRecordClick = useCallback(
    (row: OperationalRecord) => {
      if (row.entity_type && row.id) {
        openExplorerFromRecord(openDrawer, row);
      }
    },
    [openDrawer]
  );

  if (!open || !target) return null;

  const summary =
    (detail?.summary as Record<string, unknown>) ??
    (overview?.summary as Record<string, unknown>) ??
    {};
  const severity = String(summary.severity ?? overview?.risk_status ?? "");
  const showSkeleton = overviewLoading && !overview && !detail;

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
        <DrawerHeader
          title={displayTitle}
          entityType={entityType}
          entityId={entityId}
          severity={severity}
          onClose={closeDrawer}
        />

        <div className="flex-1 overflow-y-auto px-4 py-3">
          {showSkeleton && <ExplorerDrawerSkeleton />}
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
          {!error && (
            <div className="space-y-4 text-xs text-slate-300">
              <ExplorerOperationalSummary
                title={displayTitle}
                summary={String(summary.body ?? "")}
                count={Number(overview?.record_count ?? records.length)}
                status={severity}
                riskScore={overview?.risk_score as string | number | undefined}
                topStates={(overview?.top_states as string[]) ?? []}
                topOrganisations={(overview?.top_organisations as string[]) ?? []}
                updatedAt={String(overview?.updated_at ?? "")}
              />
              {slowLoad && sectionsLoading && records.length === 0 ? (
                <p className="text-[11px] text-amber-300/90">Still loading records…</p>
              ) : null}
              {showRetry && sectionsLoading ? (
                <button type="button" className="text-xs text-sovereign-accent hover:underline" onClick={() => void load()}>
                  Retry loading
                </button>
              ) : null}
              {sectionsLoading && !detail && !overview ? (
                <ExplorerDrawerSkeleton />
              ) : (
                <>
                  <ExplorerRiskFactors risk={risk} />
                  <ExplorerRecordsTable
                    records={records}
                    filter={filter}
                    onFilterChange={setFilter}
                    onRowClick={target.contextKey ? onRecordClick : undefined}
                  />
                  <section>
                    <h4 className="text-[11px] font-semibold uppercase text-slate-400">Timeline</h4>
                    <div className="mt-2">
                      {sectionsLoading && timeline.length === 0 ? (
                        <p className="text-slate-500">Loading…</p>
                      ) : (
                        <ExplorerTimelineCard items={timeline} />
                      )}
                    </div>
                  </section>
                  <section>
                    <h4 className="text-[11px] font-semibold uppercase text-slate-400">Evidence</h4>
                    <div className="mt-2">
                      <ExplorerEvidencePanel items={evidence} />
                    </div>
                  </section>
                  <section>
                    <h4 className="text-[11px] font-semibold uppercase text-slate-400">Related entities</h4>
                    <RelatedSection related={related} />
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
            href={explorerFullPageHref(target)}
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
        }}
      />
    </div>
  );
}

function DrawerHeader({
  title,
  entityType,
  entityId,
  severity,
  onClose,
}: {
  title: string;
  entityType: string;
  entityId: string;
  severity: string;
  onClose: () => void;
}) {
  return (
    <div className="flex items-start justify-between border-b border-sovereign-800 px-4 py-3">
      <div>
        <p id="explorer-drawer-title" className="text-sm font-semibold text-white">
          {title}
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
        onClick={onClose}
        className="rounded-lg border border-sovereign-700 px-2 py-1 text-xs text-slate-300 hover:bg-sovereign-800"
      >
        Close
      </button>
    </div>
  );
}

function RelatedSection({ related }: { related: Record<string, unknown> | null }) {
  return (
    <div className="mt-2">
      <ExplorerRelatedCards related={related} />
    </div>
  );
}

export const IntelligenceDetailDrawer = memo(IntelligenceDetailDrawerInner);
