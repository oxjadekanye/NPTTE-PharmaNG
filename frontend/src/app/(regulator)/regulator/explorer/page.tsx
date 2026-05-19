"use client";

import Link from "next/link";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";

const AGGREGATES = [
  ["national_risk", "national-risk-current", "Current national risk"],
  ["national_risk", "counterfeit-detections-current", "Counterfeit detections"],
  ["national_risk", "active-investigations-current", "Active investigations"],
  ["alert", "open-alerts-current", "Open alerts"],
  ["task", "command-activity-current", "Command activity"],
];

export default function ExplorerHubPage() {
  return (
    <RegulatorGuard>
      <CommandShell title="Operational drill-down explorer">
        <p className="mb-6 text-sm text-slate-400">
          Select an aggregate or open any clickable card from the national overview, command center, or executive
          mode. Full detail uses the Phase 19 explorer API.
        </p>
        <ul className="space-y-2 text-sm">
          {AGGREGATES.map(([type, id, label]) => (
            <li key={id}>
              <Link
                href={`/regulator/explorer/${encodeURIComponent(type)}/${encodeURIComponent(id)}`}
                className="text-sovereign-accent hover:underline"
              >
                {label}
              </Link>
              <span className="ml-2 text-xs text-slate-500">
                {type}/{id}
              </span>
            </li>
          ))}
        </ul>
      </CommandShell>
    </RegulatorGuard>
  );
}
