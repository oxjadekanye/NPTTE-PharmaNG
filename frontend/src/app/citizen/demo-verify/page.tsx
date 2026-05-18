"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchTraceabilityStory } from "@/services/traceability-demo";
import { publicVerify } from "@/services/citizen";

const SCENARIO_STYLES: Record<string, string> = {
  authentic: "border-emerald-500/50 bg-emerald-500/10",
  recalled: "border-rose-500/50 bg-rose-500/15",
  suspicious: "border-amber-500/50 bg-amber-500/10",
  expired: "border-slate-500/50 bg-slate-800/50",
  invalid: "border-red-500/50 bg-red-500/10",
};

export default function CitizenDemoVerifyPage() {
  const [serials, setSerials] = useState<Record<string, string>>({});
  const [results, setResults] = useState<Record<string, Record<string, unknown>>>({});
  const [loading, setLoading] = useState<string | null>(null);

  useEffect(() => {
    fetchTraceabilityStory()
      .then((r) => setSerials(r.data.demo_serials ?? {}))
      .catch(() => {});
  }, []);

  async function verify(label: string, serial: string) {
    setLoading(label);
    try {
      const res = await publicVerify({ serial_number: serial });
      setResults((prev) => ({ ...prev, [label]: res.data as Record<string, unknown> }));
    } catch {
      setResults((prev) => ({ ...prev, [label]: { outcome: "error" } }));
    } finally {
      setLoading(null);
    }
  }

  const entries = Object.entries(serials).length
    ? Object.entries(serials)
    : [
        ["authentic", "NG-NPTTE-TD-PARACETAMOL-2026-AUTH000001"],
        ["recalled", "NG-NPTTE-TD-AMOXICILLIN-2026-RECALL000001"],
        ["suspicious", "NG-NPTTE-TD-METFORMIN-2026-SUSPIC000001"],
        ["expired", "NG-NPTTE-TD-PARACETAMOL-2025-EXP0000001"],
        ["invalid", "NG-NPTTE-TD-INVALID-000000001"],
      ];

  return (
    <div className="min-h-screen bg-sovereign-950 px-4 py-8 text-slate-100 sm:px-6">
      <Link href="/citizen" className="text-[10px] uppercase tracking-widest text-sovereign-accent">
        ← Citizen portal
      </Link>
      <h1 className="mt-2 text-2xl font-semibold">Demo verification serials</h1>
      <p className="mt-2 max-w-lg text-sm text-slate-500">
        Tap a scenario to verify against the live national registry. Seed data with{" "}
        <span className="font-mono text-xs">seed_traceability_demo</span> on the backend.
      </p>

      <ul className="mx-auto mt-8 max-w-lg space-y-4">
        {entries.map(([label, serial]) => (
          <li
            key={label}
            className={`rounded-xl border p-4 ${SCENARIO_STYLES[label] ?? "border-sovereign-800"}`}
          >
            <p className="text-xs uppercase tracking-widest text-slate-400">{label}</p>
            <p className="mt-1 break-all font-mono text-xs">{serial}</p>
            <button
              type="button"
              disabled={loading === label}
              onClick={() => verify(label, serial)}
              className="mt-3 w-full rounded-lg bg-sovereign-accent py-2 text-sm font-semibold text-sovereign-950 disabled:opacity-50"
            >
              {loading === label ? "Verifying…" : "Verify now"}
            </button>
            {results[label] && (
              <p className="mt-2 text-sm">
                Outcome: <span className="font-mono">{String(results[label].outcome)}</span>
              </p>
            )}
          </li>
        ))}
      </ul>

      <Link href="/citizen/scan" className="mt-8 inline-block text-sm text-sovereign-accent hover:underline">
        Open camera scan →
      </Link>
    </div>
  );
}
