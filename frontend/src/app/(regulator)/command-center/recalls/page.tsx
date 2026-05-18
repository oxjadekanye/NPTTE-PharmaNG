"use client";

import { useMemo, useState } from "react";
import dynamic from "next/dynamic";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { ACTIVE_RECALLS, STATE_RISKS } from "@/demo/nigeria-intelligence";
import { GlassPanel } from "@/components/enterprise/GlassPanel";

const NigeriaThreatMap = dynamic(
  () => import("@/components/maps/NigeriaThreatMap").then((m) => m.NigeriaThreatMap),
  { ssr: false, loading: () => <div className="h-64 animate-pulse rounded-xl bg-sovereign-900" /> }
);

export default function NationalRecallCenterPage() {
  const [ack, setAck] = useState<Record<string, number>>(() =>
    Object.fromEntries(ACTIVE_RECALLS.map((r) => [r.recallNumber, 62 + Math.floor(Math.random() * 20)]))
  );

  const affectedPharmacies = useMemo(
    () => STATE_RISKS.reduce((sum, s) => sum + Math.floor(s.pharmacyCount * 0.08), 0),
    []
  );

  return (
    <RegulatorGuard>
      <CommandShell title="National Recall Operations Center">
        <div className="space-y-6">
          <div className="grid gap-4 lg:grid-cols-4">
            <Stat label="Nationwide broadcasts" value={ACTIVE_RECALLS.length} hint="Active programmes" />
            <Stat label="Est. affected pharmacies" value={affectedPharmacies} hint="Modelled reach" />
            <Stat label="Patient exposure (est.)" value={428_000} hint="Deterministic demo" />
            <Stat label="Destruction confirmations" value={118} hint="Awaiting final QA" />
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            {ACTIVE_RECALLS.map((r) => (
              <GlassPanel key={r.recallNumber} title={r.recallNumber} subtitle={r.product}>
                <div className="flex flex-wrap gap-2 text-[10px] uppercase text-slate-500">
                  {r.states.map((s) => (
                    <span key={s} className="rounded border border-sovereign-700 px-2 py-0.5 text-slate-300">
                      {s}
                    </span>
                  ))}
                </div>
                <div className="mt-4">
                  <div className="flex justify-between text-xs text-slate-400">
                    <span>Pharmacy acknowledgement</span>
                    <span>{ack[r.recallNumber] ?? 0}%</span>
                  </div>
                  <div className="mt-1 h-2 overflow-hidden rounded-full bg-sovereign-800">
                    <div
                      className="h-full rounded-full bg-sovereign-accent transition-all"
                      style={{ width: `${ack[r.recallNumber] ?? 0}%` }}
                    />
                  </div>
                </div>
                <div className="mt-4 flex flex-wrap gap-2">
                  <button
                    type="button"
                    className="rounded-lg border border-sovereign-600 px-3 py-1.5 text-xs hover:border-sovereign-accent"
                    onClick={() =>
                      setAck((m) => ({
                        ...m,
                        [r.recallNumber]: Math.min(100, (m[r.recallNumber] ?? 0) + 4),
                      }))
                    }
                  >
                    Simulate ACK wave
                  </button>
                  <button
                    type="button"
                    className="rounded-lg border border-sovereign-600 px-3 py-1.5 text-xs hover:border-sovereign-accent"
                  >
                    Regulator escalation
                  </button>
                  <button
                    type="button"
                    className="rounded-lg border border-sovereign-600 px-3 py-1.5 text-xs hover:border-sovereign-accent"
                  >
                    Destruction confirmation
                  </button>
                </div>
              </GlassPanel>
            ))}
          </div>

          <GlassPanel title="Live recall spread map" subtitle="Sovereign intelligence overlay (DEMO)">
            <NigeriaThreatMap />
          </GlassPanel>
        </div>
      </CommandShell>
    </RegulatorGuard>
  );
}

function Stat({ label, value, hint }: { label: string; value: number; hint: string }) {
  return (
    <div className="glass-panel rounded-xl border border-sovereign-800 p-4">
      <p className="text-[10px] uppercase tracking-wider text-slate-500">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-white">{value.toLocaleString()}</p>
      <p className="mt-1 text-[10px] text-slate-600">{hint}</p>
    </div>
  );
}
