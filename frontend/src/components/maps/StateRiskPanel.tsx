"use client";

import clsx from "clsx";
import type { DemoStateRisk } from "@/demo/types";

export function StateRiskPanel({
  states,
  selected,
  onSelect,
}: {
  states: DemoStateRisk[];
  selected?: string;
  onSelect?: (s: DemoStateRisk) => void;
}) {
  return (
    <div className="rounded-xl border border-sovereign-800 bg-sovereign-900/80 p-4">
      <h3 className="text-sm font-semibold text-white">State risk index</h3>
      <p className="mb-3 text-[10px] text-slate-500">Click state for details (DEMO)</p>
      <ul className="max-h-80 space-y-1 overflow-y-auto">
        {states.map((s) => (
          <li key={s.code}>
            <button
              type="button"
              onClick={() => onSelect?.(s)}
              className={clsx(
                "w-full rounded-lg px-3 py-2 text-left text-sm transition",
                selected === s.state
                  ? "bg-sovereign-accent/20 text-white"
                  : "hover:bg-sovereign-800 text-slate-300"
              )}
            >
              <div className="flex justify-between">
                <span>{s.state}</span>
                <span
                  className={clsx(
                    "font-mono text-xs",
                    s.riskScore >= 70 ? "text-red-400" : s.riskScore >= 50 ? "text-amber-400" : "text-emerald-400"
                  )}
                >
                  {s.riskScore}
                </span>
              </div>
              <p className="text-[10px] text-slate-500">
                CF {s.counterfeitCount} · shortage {s.shortageCount} · pharmacies {s.pharmacyCount}
              </p>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
