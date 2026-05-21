"use client";

import { useEffect, useState } from "react";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { OperationalSkeleton } from "@/components/ui/OperationalSkeleton";
import { fetchNationalOperationsMetrics } from "@/services/national-operations";

export default function ExecutiveNationalOpsPage() {
  const [metrics, setMetrics] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    fetchNationalOperationsMetrics().then((r) => {
      if (r.success) setMetrics(r.data ?? null);
    });
  }, []);

  const cards = metrics
    ? [
        { label: "Medicine shortage index", value: metrics.medicine_shortage_index },
        { label: "Counterfeit risk heat", value: metrics.counterfeit_risk_heat_score },
        { label: "Operational readiness", value: metrics.national_operational_readiness_score },
        { label: "Border threat score", value: metrics.border_threat_score },
        { label: "Emergency medicine readiness", value: metrics.emergency_medicine_readiness },
        { label: "Import dependency index", value: metrics.import_dependency_index },
      ]
    : [];

  return (
    <RegulatorGuard>
      <CommandShell title="National operations intelligence">
        <p className="mb-4 text-sm text-slate-400">Executive drilldown · export-ready cards</p>
        {!metrics ? (
          <OperationalSkeleton rows={6} />
        ) : (
          <>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {cards.map((c) => (
                <div
                  key={c.label}
                  className="rounded-xl border border-indigo-500/30 bg-indigo-950/30 p-4"
                >
                  <p className="text-xs uppercase tracking-wider text-indigo-300/80">{c.label}</p>
                  <p className="mt-2 text-3xl font-bold text-white">{String(c.value)}</p>
                </div>
              ))}
            </div>
            <p className="mt-6 text-xs text-slate-500">{String(metrics.disclaimer)}</p>
            <section className="mt-8">
              <h3 className="text-sm font-semibold text-slate-300">State compliance</h3>
              <ul className="mt-2 space-y-1 text-sm text-slate-400">
                {((metrics.state_compliance as { state: string; compliance_score: number }[]) ?? []).map(
                  (s) => (
                    <li key={s.state}>
                      {s.state}: {s.compliance_score}% compliance
                    </li>
                  )
                )}
              </ul>
            </section>
          </>
        )}
      </CommandShell>
    </RegulatorGuard>
  );
}
