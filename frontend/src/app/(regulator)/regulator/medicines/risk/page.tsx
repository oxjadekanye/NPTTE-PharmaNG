"use client";

import { useEffect, useState } from "react";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { fetchCounterfeitRisk, fetchShortageRisk } from "@/services/medicine-intelligence";

export default function MedicineRiskDashboardPage() {
  const [shortage, setShortage] = useState<Record<string, unknown> | null>(null);
  const [counterfeit, setCounterfeit] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    Promise.all([fetchShortageRisk(), fetchCounterfeitRisk()]).then(([s, c]) => {
      if (s.success) setShortage(s.data ?? null);
      if (c.success) setCounterfeit(c.data ?? null);
    });
  }, []);

  return (
    <RegulatorGuard>
      <CommandShell title="National medicine risk" subtitle="Shortage & counterfeit intelligence">
        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-xl border border-amber-500/30 bg-amber-500/5 p-4">
            <p className="text-xs uppercase text-amber-200/80">Shortage index</p>
            <p className="mt-2 text-3xl font-bold text-white">
              {String((shortage as { shortage_risk_index?: number })?.shortage_risk_index ?? "—")}
            </p>
          </div>
          <div className="rounded-xl border border-rose-500/30 bg-rose-500/5 p-4">
            <p className="text-xs uppercase text-rose-200/80">Counterfeit heat</p>
            <p className="mt-2 text-3xl font-bold text-white">
              {String(
                (counterfeit?.summary as { counterfeit_heat_score?: number })?.counterfeit_heat_score ?? "—"
              )}
            </p>
          </div>
        </div>
      </CommandShell>
    </RegulatorGuard>
  );
}
