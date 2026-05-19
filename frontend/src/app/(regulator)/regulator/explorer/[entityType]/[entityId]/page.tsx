"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import {
  executeExplorerAction,
  fetchExplorerActions,
  fetchExplorerDetail,
  fetchExplorerEvidence,
  fetchExplorerOverviewCached,
  fetchExplorerRelated,
  fetchExplorerRiskBreakdown,
  fetchExplorerTimeline,
} from "@/services/explorer";
import { recordSearchText } from "@/services/explorer-format";
import { ExplorerCopilotPlaceholder } from "@/components/explorer/ExplorerCopilotPlaceholder";
import { ExplorerEvidencePanel } from "@/components/explorer/renderers/ExplorerEvidencePanel";
import { ExplorerOperationalSummary } from "@/components/explorer/renderers/ExplorerOperationalSummary";
import { ExplorerRecordsTable } from "@/components/explorer/renderers/ExplorerRecordsTable";
import { ExplorerRiskFactors } from "@/components/explorer/renderers/ExplorerRiskFactors";
import { ExplorerTimelineCard } from "@/components/explorer/renderers/ExplorerTimelineCard";
import { ExplorerRelatedCards } from "@/components/explorer/ExplorerRelatedCards";

export default function ExplorerEntityDetailPage() {
  const params = useParams<{ entityType: string; entityId: string }>();
  const entityType = decodeURIComponent(params.entityType ?? "");
  const entityId = decodeURIComponent(params.entityId ?? "");
  const [overview, setOverview] = useState<Record<string, unknown> | null>(null);
  const [detail, setDetail] = useState<Record<string, unknown> | null>(null);
  const [risk, setRisk] = useState<Record<string, unknown> | null>(null);
  const [related, setRelated] = useState<Record<string, unknown> | null>(null);
  const [timeline, setTimeline] = useState<Record<string, unknown>[]>([]);
  const [evidence, setEvidence] = useState<Record<string, unknown>[]>([]);
  const [actions, setActions] = useState<{ id: string; label: string; requires_confirm?: boolean }[]>([]);
  const [search, setSearch] = useState("");
  const [msg, setMsg] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    void fetchExplorerOverviewCached(entityType, entityId).then((ov) => {
      if (!cancelled && ov.success && ov.data) setOverview(ov.data as Record<string, unknown>);
    });
    void fetchExplorerDetail(entityType, entityId, 1, 25).then((d) => {
      if (!cancelled && d.success) setDetail(d.data as Record<string, unknown>);
    });
    void Promise.all([
      fetchExplorerRiskBreakdown(entityType, entityId).catch(() => null),
      fetchExplorerRelated(entityType, entityId).catch(() => null),
      fetchExplorerTimeline(entityType, entityId).catch(() => null),
      fetchExplorerEvidence(entityType, entityId).catch(() => null),
      fetchExplorerActions(entityType, entityId).catch(() => null),
    ]).then(([r, rel, t, e, a]) => {
      if (cancelled) return;
      if (r?.success) setRisk(r.data as Record<string, unknown>);
      if (rel?.success) setRelated((rel.data as { related_entities?: Record<string, unknown> })?.related_entities ?? null);
      const tSlice = (t?.data as { timeline?: { items?: unknown[] } })?.timeline;
      setTimeline((tSlice?.items ?? []) as Record<string, unknown>[]);
      const eSlice = (e?.data as { evidence?: { items?: unknown[] } })?.evidence;
      setEvidence((eSlice?.items ?? []) as Record<string, unknown>[]);
      setActions((a?.data as { actions?: typeof actions })?.actions ?? []);
    });
    return () => {
      cancelled = true;
    };
  }, [entityType, entityId]);

  const records = useMemo(() => {
    const raw = (detail?.records as Record<string, unknown>[]) ?? [];
    if (!search.trim()) return raw;
    const q = search.toLowerCase();
    return raw.filter((row) => recordSearchText(row).includes(q));
  }, [detail, search]);

  const summary = (detail?.summary as Record<string, unknown>) ?? (overview?.summary as Record<string, unknown>) ?? {};

  return (
    <RegulatorGuard>
      <CommandShell title="Explorer detail">
        <div className="mb-4 flex flex-wrap gap-3 text-xs">
          <Link href="/regulator/explorer" className="text-sovereign-accent hover:underline">
            ← Explorer hub
          </Link>
          <Link href="/regulator" className="text-sovereign-accent hover:underline">
            National overview
          </Link>
        </div>
        <div className="rounded-xl border border-sovereign-800 bg-sovereign-900/50 p-4">
          <h1 className="text-lg font-semibold text-white">{String(summary.title ?? "Operational detail")}</h1>
          <p className="text-xs text-slate-500">
            {entityType} · {entityId}
          </p>
          {summary.body != null && String(summary.body).length > 0 && (
            <p className="mt-3 text-sm text-slate-300">{String(summary.body)}</p>
          )}
        </div>

        <div className="mt-6 space-y-4">
          <ExplorerRiskFactors risk={risk ?? (detail?.risk_explanation as Record<string, unknown>) ?? null} />
          <ExplorerRecordsTable records={records} filter={search} onFilterChange={setSearch} />
          <section className="rounded-xl border border-sovereign-800 p-3">
            <h2 className="text-xs font-semibold uppercase text-slate-400">Related entities</h2>
            <div className="mt-2">
              <ExplorerRelatedCards
                related={(related ?? (detail?.related_entities as Record<string, unknown>)) ?? null}
              />
            </div>
          </section>
          <section className="rounded-xl border border-sovereign-800 p-3">
            <h2 className="text-xs font-semibold uppercase text-slate-400">Timeline</h2>
            <div className="mt-2">
              <ExplorerTimelineCard items={timeline} />
            </div>
          </section>
          <section className="rounded-xl border border-sovereign-800 p-3">
            <h2 className="text-xs font-semibold uppercase text-slate-400">Evidence</h2>
            <div className="mt-2">
              <ExplorerEvidencePanel items={evidence} />
            </div>
          </section>
          <ExplorerCopilotPlaceholder />
        </div>

        <section className="mt-6 rounded-xl border border-sovereign-800 p-3">
          <h2 className="text-xs font-semibold uppercase text-slate-400">Actions</h2>
          {msg && <p className="mt-2 text-xs text-emerald-400">{msg}</p>}
          <ul className="mt-2 space-y-2">
            {actions.map((act) => (
              <li key={act.id}>
                <button
                  type="button"
                  className="rounded border border-sovereign-700 px-3 py-1 text-xs text-sovereign-accent hover:bg-sovereign-800"
                  onClick={async () => {
                    setMsg(null);
                    const res = await executeExplorerAction(entityType, entityId, {
                      action_id: act.id,
                      confirm: act.requires_confirm ? true : false,
                      title: `Detail page: ${act.label}`,
                    });
                    setMsg(res.success ? "Done." : res.message || "Failed");
                  }}
                >
                  {act.label}
                </button>
              </li>
            ))}
          </ul>
        </section>
      </CommandShell>
    </RegulatorGuard>
  );
}
