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
  fetchExplorerRelated,
  fetchExplorerRiskBreakdown,
  fetchExplorerTimeline,
} from "@/services/explorer";

export default function ExplorerEntityDetailPage() {
  const params = useParams<{ entityType: string; entityId: string }>();
  const entityType = decodeURIComponent(params.entityType ?? "");
  const entityId = decodeURIComponent(params.entityId ?? "");
  const [detail, setDetail] = useState<Record<string, unknown> | null>(null);
  const [risk, setRisk] = useState<Record<string, unknown> | null>(null);
  const [related, setRelated] = useState<Record<string, unknown> | null>(null);
  const [timeline, setTimeline] = useState<unknown[]>([]);
  const [evidence, setEvidence] = useState<unknown[]>([]);
  const [actions, setActions] = useState<{ id: string; label: string; requires_confirm?: boolean }[]>([]);
  const [severityFilter, setSeverityFilter] = useState("");
  const [search, setSearch] = useState("");
  const [msg, setMsg] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    Promise.all([
      fetchExplorerDetail(entityType, entityId),
      fetchExplorerRiskBreakdown(entityType, entityId).catch(() => null),
      fetchExplorerRelated(entityType, entityId).catch(() => null),
      fetchExplorerTimeline(entityType, entityId).catch(() => null),
      fetchExplorerEvidence(entityType, entityId).catch(() => null),
      fetchExplorerActions(entityType, entityId).catch(() => null),
    ]).then(([d, r, rel, t, e, a]) => {
      if (cancelled) return;
      if (d.success) setDetail(d.data as Record<string, unknown>);
      if (r?.success) setRisk(r.data as Record<string, unknown>);
      if (rel?.success) setRelated((rel.data as { related_entities?: Record<string, unknown> })?.related_entities ?? null);
      setTimeline((t?.data as { timeline?: unknown[] })?.timeline ?? []);
      setEvidence((e?.data as { evidence?: unknown[] })?.evidence ?? []);
      setActions((a?.data as { actions?: typeof actions })?.actions ?? []);
    });
    return () => {
      cancelled = true;
    };
  }, [entityType, entityId]);

  const records = useMemo(() => {
    const raw = (detail?.records as Record<string, unknown>[]) ?? [];
    return raw.filter((row) => {
      const blob = JSON.stringify(row).toLowerCase();
      if (search && !blob.includes(search.toLowerCase())) return false;
      if (severityFilter && String(row.severity ?? "").toLowerCase() !== severityFilter.toLowerCase()) return false;
      return true;
    });
  }, [detail, search, severityFilter]);

  const summary = (detail?.summary as Record<string, unknown>) ?? {};

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

        <div className="mt-4 flex flex-wrap gap-2">
          <input
            type="search"
            placeholder="Search records…"
            value={search}
            onChange={(ev) => setSearch(ev.target.value)}
            className="min-w-[180px] rounded border border-sovereign-700 bg-sovereign-900 px-2 py-1 text-xs text-white"
          />
          <input
            type="text"
            placeholder="Severity filter"
            value={severityFilter}
            onChange={(ev) => setSeverityFilter(ev.target.value)}
            className="w-32 rounded border border-sovereign-700 bg-sovereign-900 px-2 py-1 text-xs text-white"
          />
        </div>

        <div className="mt-6 grid gap-4 lg:grid-cols-2">
          <section className="rounded-xl border border-sovereign-800 p-3">
            <h2 className="text-xs font-semibold uppercase text-slate-400">Risk explanation</h2>
            <pre className="mt-2 max-h-64 overflow-auto text-[10px] text-slate-400">
              {JSON.stringify(risk ?? detail?.risk_explanation ?? {}, null, 2)}
            </pre>
          </section>
          <section className="rounded-xl border border-sovereign-800 p-3">
            <h2 className="text-xs font-semibold uppercase text-slate-400">Relationship map (Phase 19)</h2>
            <pre className="mt-2 max-h-64 overflow-auto text-[10px] text-slate-400">
              {JSON.stringify(related ?? detail?.related_entities ?? {}, null, 2)}
            </pre>
          </section>
          <section className="rounded-xl border border-sovereign-800 p-3 lg:col-span-2">
            <h2 className="text-xs font-semibold uppercase text-slate-400">Records</h2>
            <pre className="mt-2 max-h-72 overflow-auto text-[10px] text-slate-400">
              {JSON.stringify(records.slice(0, 80), null, 2)}
            </pre>
          </section>
          <section className="rounded-xl border border-sovereign-800 p-3">
            <h2 className="text-xs font-semibold uppercase text-slate-400">Timeline</h2>
            <pre className="mt-2 max-h-48 overflow-auto text-[10px] text-slate-400">
              {JSON.stringify(timeline.slice(0, 40), null, 2)}
            </pre>
          </section>
          <section className="rounded-xl border border-sovereign-800 p-3">
            <h2 className="text-xs font-semibold uppercase text-slate-400">Evidence</h2>
            <pre className="mt-2 max-h-48 overflow-auto text-[10px] text-slate-400">
              {JSON.stringify(evidence, null, 2)}
            </pre>
          </section>
        </div>

        <section className="mt-6 rounded-xl border border-dashed border-sovereign-700 p-4 text-sm text-slate-500">
          <h2 className="text-xs font-semibold uppercase text-slate-400">Phase 20 — Copilot</h2>
          <p className="mt-2">Structured LLM assist and policy grounding will attach here.</p>
        </section>

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
