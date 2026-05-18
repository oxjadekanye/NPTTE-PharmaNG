"use client";

import { useState } from "react";
import clsx from "clsx";
import type { DemoIncident } from "@/demo/types";

const ESCALATION = ["Zonal lead", "National desk", "Ministerial briefing", "Inter-agency task force"];

const ACTIONS = [
  "Regulatory hold on linked SKUs",
  "Customs manifest re-screen",
  "Pharmacy licence review",
  "Field seizure order",
  "Public advisory draft",
];

export function IncidentWorkflowPanel({ incident }: { incident: DemoIncident }) {
  const [assignee, setAssignee] = useState(incident.assignedTo);
  const [custody, setCustody] = useState<string[]>([
    `${incident.openedAt} · Event opened — chain start`,
    "Evidence bag NPTTE-EV-9921 — NAFDAC custody",
  ]);

  return (
    <div className="space-y-4">
      <div className="rounded-xl border border-sovereign-800 bg-sovereign-900/60 p-4">
        <h4 className="text-sm font-semibold text-white">Assignment &amp; escalation</h4>
        <div className="mt-3 grid gap-3 sm:grid-cols-2">
          <label className="text-xs text-slate-500">
            Lead investigator
            <select
              className="mt-1 w-full rounded-lg border border-sovereign-700 bg-sovereign-950 px-2 py-2 text-sm text-white"
              value={assignee}
              onChange={(e) => setAssignee(e.target.value)}
            >
              <option>{incident.assignedTo}</option>
              <option>Insp. Chidi Okafor</option>
              <option>Insp. Halima Yusuf</option>
              <option>ACG Tunde Williams</option>
            </select>
          </label>
          <div>
            <p className="text-xs text-slate-500">Escalation chain</p>
            <ol className="mt-2 space-y-1 text-xs text-slate-300">
              {ESCALATION.map((step, i) => (
                <li key={step} className="flex items-center gap-2">
                  <span className="font-mono text-sovereign-accent">{i + 1}</span>
                  {step}
                </li>
              ))}
            </ol>
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-sovereign-800 bg-sovereign-900/60 p-4">
        <h4 className="text-sm font-semibold text-white">Inter-agency collaboration</h4>
        <div className="mt-2 flex flex-wrap gap-2">
          {incident.regulators.map((r) => (
            <span key={r} className="rounded-full border border-sky-500/30 bg-sky-500/10 px-2 py-1 text-[10px] text-sky-200">
              {r}
            </span>
          ))}
          <span className="rounded-full border border-violet-500/30 bg-violet-500/10 px-2 py-1 text-[10px] text-violet-200">
            NPTTE Command
          </span>
        </div>
      </div>

      <div className="rounded-xl border border-sovereign-800 bg-sovereign-900/60 p-4">
        <h4 className="text-sm font-semibold text-white">Chain of custody log</h4>
        <ul className="mt-2 space-y-2 border-l border-sovereign-700 pl-3 text-xs text-slate-300">
          {custody.map((line) => (
            <li key={line}>{line}</li>
          ))}
        </ul>
        <button
          type="button"
          className="mt-3 rounded-lg border border-sovereign-600 px-3 py-1.5 text-xs text-sovereign-accent hover:bg-sovereign-800"
          onClick={() =>
            setCustody((c) => [
              ...c,
              `${new Date().toISOString()} · Custody transfer logged (UI demo — not persisted)`,
            ])
          }
        >
          Log custody transfer
        </button>
      </div>

      <div className="rounded-xl border border-sovereign-800 bg-sovereign-900/60 p-4">
        <h4 className="text-sm font-semibold text-white">Enforcement actions</h4>
        <div className="mt-2 flex flex-wrap gap-2">
          {ACTIONS.map((a) => (
            <button
              key={a}
              type="button"
              className={clsx(
                "rounded-lg border px-2 py-1 text-[10px] transition",
                "border-sovereign-600 text-slate-300 hover:border-sovereign-accent hover:text-white"
              )}
            >
              {a}
            </button>
          ))}
        </div>
        <p className="mt-2 text-[10px] text-slate-600">Actions are UI placeholders — server workflows unchanged.</p>
      </div>
    </div>
  );
}
