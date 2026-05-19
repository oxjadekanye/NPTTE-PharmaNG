"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { ExplorerActionModal, type ExplorerWorkflow } from "@/components/explorer/ExplorerActionModal";
import { ExplorerRiskPanel } from "@/components/explorer/ExplorerRiskPanel";
import { ExplorerSeverityBadge } from "@/components/explorer/ExplorerSeverityBadge";
import { fetchExplorerActions, fetchExplorerContextBundle } from "@/services/explorer";

function paginatedItems(data: Record<string, unknown> | null): Record<string, unknown>[] {
  const rec = data?.records;
  if (Array.isArray(rec)) return rec as Record<string, unknown>[];
  if (rec && typeof rec === "object" && Array.isArray((rec as { items?: unknown[] }).items)) {
    return (rec as { items: Record<string, unknown>[] }).items;
  }
  return [];
}

export default function ExplorerContextDetailPage() {
  const params = useParams<{ contextKey: string }>();
  const contextKey = decodeURIComponent(params.contextKey ?? "");
  const [bundle, setBundle] = useState<Record<string, unknown> | null>(null);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [stateFilter, setStateFilter] = useState("");
  const [severityFilter, setSeverityFilter] = useState("");
  const [actions, setActions] = useState<{ id: string; label: string; workflow?: string }[]>([]);
  const [modal, setModal] = useState<{ workflow: ExplorerWorkflow; actionId: string; label: string } | null>(
    null
  );
  const [msg, setMsg] = useState<string | null>(null);

  const route = bundle?.route as { entity_type?: string; entity_id?: string } | undefined;
  const entityType = route?.entity_type ?? "national_risk";
  const entityId = route?.entity_id ?? "national-risk-current";

  const load = useCallback(() => {
    fetchExplorerContextBundle(contextKey, page, 50).then((r) => {
      if (r.success) setBundle(r.data as Record<string, unknown>);
    });
    fetchExplorerActions(entityType, entityId).then((r) => {
      if (r.success) setActions((r.data as { actions?: typeof actions })?.actions ?? []);
    });
  }, [contextKey, page, entityType, entityId]);

  useEffect(() => {
    load();
  }, [load]);

  const records = useMemo(() => {
    let rows = paginatedItems(bundle);
    if (search.trim()) {
      const q = search.toLowerCase();
      rows = rows.filter((r) => JSON.stringify(r).toLowerCase().includes(q));
    }
    if (stateFilter) rows = rows.filter((r) => String(r.state ?? "").toLowerCase() === stateFilter.toLowerCase());
    if (severityFilter)
      rows = rows.filter((r) => String(r.severity ?? "").toLowerCase() === severityFilter.toLowerCase());
    return rows;
  }, [bundle, search, stateFilter, severityFilter]);

  const summary = (bundle?.summary as Record<string, unknown>) ?? {};

  return (
    <RegulatorGuard>
      <CommandShell title="Context intelligence">
        <div className="mb-4 flex flex-wrap gap-3 text-xs">
          <Link href="/regulator/explorer" className="text-sovereign-accent hover:underline">
            ← Explorer hub
          </Link>
          <Link href="/regulator" className="text-sovereign-accent hover:underline">
            National overview
          </Link>
        </div>

        <div className="rounded-xl border border-sovereign-800 bg-sovereign-900/50 p-4">
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="text-lg font-semibold text-white">{String(summary.title ?? contextKey)}</h1>
            {summary.severity != null && <ExplorerSeverityBadge severity={String(summary.severity)} />}
            {summary.count != null && (
              <span className="text-xs text-slate-500">{String(summary.count)} records</span>
            )}
          </div>
          {summary.body != null && String(summary.body).length > 0 && (
            <p className="mt-2 text-sm text-slate-300">{String(summary.body)}</p>
          )}
        </div>

        <ExplorerRiskPanel risk={(bundle?.risk_explanation as Record<string, unknown>) ?? null} />

        <div className="mt-4 flex flex-wrap gap-2">
          <input
            type="search"
            placeholder="Search organisation, serial, product…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="min-w-[200px] flex-1 rounded border border-sovereign-700 bg-sovereign-900 px-2 py-1 text-xs text-white"
          />
          <input
            placeholder="State"
            value={stateFilter}
            onChange={(e) => setStateFilter(e.target.value)}
            className="w-28 rounded border border-sovereign-700 bg-sovereign-900 px-2 py-1 text-xs text-white"
          />
          <input
            placeholder="Severity"
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="w-28 rounded border border-sovereign-700 bg-sovereign-900 px-2 py-1 text-xs text-white"
          />
        </div>

        <div className="mt-4 overflow-auto rounded border border-sovereign-800">
          <table className="w-full text-left text-[11px]">
            <thead className="sticky top-0 bg-sovereign-900 text-slate-500">
              <tr>
                <th className="px-2 py-2">Incident</th>
                <th className="px-2 py-2">Severity</th>
                <th className="px-2 py-2">Organisation</th>
                <th className="px-2 py-2">Location</th>
                <th className="px-2 py-2">Product</th>
                <th className="px-2 py-2">Officer</th>
                <th className="px-2 py-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {records.length === 0 && (
                <tr>
                  <td colSpan={7} className="px-2 py-6 text-center text-slate-500">
                    No records — run <code className="text-sovereign-accent">seed_operational_demo_data</code>
                  </td>
                </tr>
              )}
              {records.map((row) => (
                <tr key={String(row.id)} className="border-t border-sovereign-800/80 hover:bg-sovereign-800/30">
                  <td className="px-2 py-2 text-slate-200">{String(row.title ?? "—")}</td>
                  <td className="px-2 py-2">{String(row.severity ?? "—")}</td>
                  <td className="px-2 py-2">{String(row.organisation ?? "—")}</td>
                  <td className="px-2 py-2">
                    {String(row.city ?? "")}
                    {row.state ? `, ${row.state}` : ""}
                  </td>
                  <td className="px-2 py-2">{String(row.product ?? "—")}</td>
                  <td className="px-2 py-2">{String(row.assigned_officer ?? "—")}</td>
                  <td className="px-2 py-2">{String(row.action_status ?? row.status ?? "—")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="mt-4 flex items-center justify-between">
          <button
            type="button"
            disabled={page <= 1}
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            className="rounded border border-sovereign-700 px-2 py-1 text-xs disabled:opacity-40"
          >
            Previous
          </button>
          <span className="text-xs text-slate-500">Page {page}</span>
          <button
            type="button"
            onClick={() => setPage((p) => p + 1)}
            className="rounded border border-sovereign-700 px-2 py-1 text-xs"
          >
            Next
          </button>
        </div>

        {msg && <p className="mt-3 text-sm text-emerald-400">{msg}</p>}
        <section className="mt-6">
          <h2 className="text-xs font-semibold uppercase text-slate-400">Actions</h2>
          <ul className="mt-2 flex flex-wrap gap-2">
            {actions.map((a) => (
              <li key={a.id}>
                <button
                  type="button"
                  className="rounded border border-sovereign-700 px-3 py-1 text-xs text-sovereign-accent hover:bg-sovereign-800"
                  onClick={() =>
                    setModal({
                      workflow: (a.workflow as ExplorerWorkflow) || "task",
                      actionId: a.id,
                      label: a.label,
                    })
                  }
                >
                  {a.label}
                </button>
              </li>
            ))}
          </ul>
        </section>

        <ExplorerActionModal
          open={Boolean(modal)}
          workflow={modal?.workflow ?? null}
          entityType={entityType}
          entityId={entityId}
          actionId={modal?.actionId ?? ""}
          actionLabel={modal?.label ?? ""}
          onClose={() => setModal(null)}
          onSuccess={(m) => {
            setMsg(m);
            load();
          }}
        />
      </CommandShell>
    </RegulatorGuard>
  );
}
