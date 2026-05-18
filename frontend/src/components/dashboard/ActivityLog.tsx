"use client";

import { useCommandStore } from "@/store/command-store";

export function ActivityLog() {
  const log = useCommandStore((s) => s.activityLog);

  return (
    <div className="rounded-xl border border-sovereign-800 bg-sovereign-900/60 p-4">
      <h3 className="text-sm font-semibold text-white">Command activity</h3>
      <p className="mb-3 text-[10px] text-slate-500">Simulated operational log (DEMO)</p>
      <ul className="max-h-40 space-y-1 overflow-y-auto font-mono text-xs text-slate-400">
        {log.map((line, i) => (
          <li key={`${line}-${i}`}>{line}</li>
        ))}
      </ul>
    </div>
  );
}
