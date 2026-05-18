"use client";

import { ACTIVE_RECALLS, BLACKLISTED_BATCHES } from "@/demo/nigeria-intelligence";

export function IntelligenceHighlights() {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <div className="rounded-xl border border-red-500/30 bg-red-950/20 p-4">
        <h3 className="text-sm font-semibold text-red-200">Emergency recalls (DEMO)</h3>
        <ul className="mt-3 space-y-2 text-sm text-slate-300">
          {ACTIVE_RECALLS.map((r) => (
            <li key={r.recallNumber}>
              <span className="font-mono text-xs text-red-300">{r.recallNumber}</span> — {r.product}
              <span className="ml-2 text-xs text-slate-500">({r.states.join(", ")})</span>
            </li>
          ))}
        </ul>
      </div>
      <div className="rounded-xl border border-sovereign-800 bg-sovereign-900/60 p-4">
        <h3 className="text-sm font-semibold text-white">Blacklisted batches (DEMO)</h3>
        <ul className="mt-3 space-y-2 text-sm text-slate-300">
          {BLACKLISTED_BATCHES.map((b) => (
            <li key={b.batchNumber}>
              <span className="font-mono text-xs text-amber-300">{b.batchNumber}</span>
              <p className="text-xs text-slate-500">{b.reason}</p>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
