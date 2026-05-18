"use client";

import { useState } from "react";
import clsx from "clsx";
import { DEMO_INCIDENTS } from "@/demo/nigeria-intelligence";
import type { DemoIncident } from "@/demo/types";
import type { IncidentRow } from "@/shared/types";

function mergeIncidents(api: IncidentRow[]): DemoIncident[] {
  if (api.length === 0) return DEMO_INCIDENTS;
  return api.map((row) => {
    const demo = DEMO_INCIDENTS.find((d) => d.code === row.code);
    if (demo) return demo;
    return {
      id: row.id,
      code: row.code,
      title: row.title,
      category: "operational",
      severity: (row.severity as DemoIncident["severity"]) || "medium",
      status: (row.status as DemoIncident["status"]) || "open",
      state: "—",
      city: "—",
      assignedTo: "Unassigned",
      agency: "NAFDAC",
      threatScore: Number(row.threat_score) || 0,
      openedAt: new Date().toISOString(),
      linkedPharmacies: [],
      linkedBatches: [],
      linkedSuppliers: [],
      regulators: ["NAFDAC"],
      inspectors: [],
      timeline: [{ at: "—", event: "Loaded from national API" }],
    };
  });
}

const severityBadge: Record<string, string> = {
  low: "bg-slate-600/30 text-slate-300",
  medium: "bg-amber-500/20 text-amber-200",
  high: "bg-orange-500/20 text-orange-200",
  critical: "bg-red-500/25 text-red-200",
};

export function IncidentCenter({ apiIncidents = [] }: { apiIncidents?: IncidentRow[] }) {
  const incidents = mergeIncidents(apiIncidents);
  const [selected, setSelected] = useState<DemoIncident>(incidents[0]);

  return (
    <div className="grid gap-6 lg:grid-cols-5">
      <div className="lg:col-span-2">
        <div className="overflow-hidden rounded-xl border border-sovereign-800 shadow-lg">
          <table className="w-full text-left text-sm">
            <thead className="bg-sovereign-900 text-xs uppercase text-slate-500">
              <tr>
                <th className="px-3 py-2">Code</th>
                <th className="px-3 py-2">Severity</th>
                <th className="px-3 py-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {incidents.map((inc) => (
                <tr
                  key={inc.id}
                  onClick={() => setSelected(inc)}
                  className={clsx(
                    "cursor-pointer border-t border-sovereign-800 transition hover:bg-sovereign-800/50",
                    selected.id === inc.id && "bg-sovereign-accent/10"
                  )}
                >
                  <td className="px-3 py-2 font-mono text-[10px]">{inc.code}</td>
                  <td className="px-3 py-2">
                    <span className={clsx("rounded px-1.5 py-0.5 text-[10px] uppercase", severityBadge[inc.severity])}>
                      {inc.severity}
                    </span>
                  </td>
                  <td className="px-3 py-2 capitalize text-slate-400">{inc.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      <div className="space-y-4 lg:col-span-3">
        <div className="rounded-xl border border-sovereign-800 bg-sovereign-900/60 p-5 shadow-lg">
          <h3 className="text-lg font-semibold text-white">{selected.title}</h3>
          <p className="mt-1 text-xs text-slate-500">
            {selected.city}, {selected.state} · {selected.agency} · Threat {selected.threatScore}
          </p>
          <div className="mt-4 grid gap-3 sm:grid-cols-2 text-sm">
            <div>
              <p className="text-xs text-slate-500">Assigned</p>
              <p>{selected.assignedTo}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500">Escalation</p>
              <p className="capitalize">{selected.status}</p>
            </div>
          </div>
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          <LinkPanel title="Linked pharmacies" items={selected.linkedPharmacies} />
          <LinkPanel title="Linked batches" items={selected.linkedBatches} />
          <LinkPanel title="Linked suppliers" items={selected.linkedSuppliers} />
          <LinkPanel title="Regulators / inspectors" items={[...selected.regulators, ...selected.inspectors]} />
        </div>
        <div className="rounded-xl border border-sovereign-800 bg-sovereign-900/60 p-4">
          <h4 className="text-sm font-semibold text-white">Resolution timeline &amp; audit</h4>
          <ul className="mt-3 space-y-2 border-l border-sovereign-700 pl-4">
            {selected.timeline.map((t) => (
              <li key={`${t.at}-${t.event}`} className="text-sm text-slate-300">
                <span className="font-mono text-xs text-sovereign-accent">{t.at}</span> — {t.event}
              </li>
            ))}
          </ul>
        </div>
        <div className="rounded-xl border border-dashed border-sovereign-700 bg-sovereign-950/50 p-4 text-center text-sm text-slate-500">
          Evidence upload — UI placeholder only (no file storage in demo mode)
        </div>
      </div>
    </div>
  );
}

function LinkPanel({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="rounded-lg border border-sovereign-800 bg-sovereign-900/40 p-3">
      <p className="text-xs font-medium uppercase text-slate-500">{title}</p>
      {items.length === 0 ? (
        <p className="mt-2 text-xs text-slate-600">None linked</p>
      ) : (
        <ul className="mt-2 space-y-1 text-sm text-slate-300">
          {items.map((x) => (
            <li key={x}>{x}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
