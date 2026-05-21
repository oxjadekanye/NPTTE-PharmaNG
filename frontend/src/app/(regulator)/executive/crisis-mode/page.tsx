"use client";

import { useEffect, useState } from "react";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { activateCrisis, fetchCrisisStatus } from "@/services/crisis-mode";

const SCENARIOS = [
  "counterfeit_outbreak",
  "medicine_shortage",
  "border_seizure",
  "emergency_recall",
  "contamination_alert",
] as const;

export default function CrisisModePage() {
  const [status, setStatus] = useState<Record<string, unknown> | null>(null);
  const [msg, setMsg] = useState<string | null>(null);

  useEffect(() => {
    fetchCrisisStatus().then((r) => {
      if (r.success) setStatus(r.data ?? null);
    });
  }, []);

  const onActivate = async (scenario: string) => {
    setMsg(null);
    const r = await activateCrisis(scenario);
    setMsg(r.success ? `Activated: ${scenario}` : r.message);
    const s = await fetchCrisisStatus();
    if (s.success) setStatus(s.data ?? null);
  };

  return (
    <RegulatorGuard>
      <CommandShell title="Executive crisis mode">
        <p className="mb-4 text-sm text-slate-400">Sovereign emergency command activation</p>
        <div
          className={`mb-6 rounded-xl border px-4 py-3 ${
            status?.active ? "border-rose-500/50 bg-rose-500/10" : "border-sovereign-700"
          }`}
        >
          <p className="text-sm text-white">
            Status: {status?.active ? "CRISIS ACTIVE" : "Normal readiness"}
          </p>
          {status?.title ? <p className="text-xs text-slate-400">{String(status.title)}</p> : null}
        </div>
        <div className="flex flex-wrap gap-2">
          {SCENARIOS.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => void onActivate(s)}
              className="rounded-lg border border-amber-500/40 bg-amber-500/10 px-3 py-2 text-xs text-amber-100 hover:bg-amber-500/20"
            >
              {s.replace(/_/g, " ")}
            </button>
          ))}
        </div>
        {msg && <p className="mt-4 text-sm text-emerald-300">{msg}</p>}
      </CommandShell>
    </RegulatorGuard>
  );
}
