"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { OperationalSkeleton } from "@/components/ui/OperationalSkeleton";
import { fetchMedicineIntelligence } from "@/services/medicine-intelligence";

export default function MedicineIntelligencePage() {
  const [rows, setRows] = useState<unknown[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMedicineIntelligence()
      .then((r) => setRows(r.data?.medicines ?? []))
      .finally(() => setLoading(false));
  }, []);

  return (
    <RegulatorGuard>
      <CommandShell title="Medicine intelligence">
        <p className="mb-4 text-sm text-slate-400">National pharmaceutical risk profiles</p>
        <Link href="/regulator/medicines/risk" className="mb-4 inline-block text-xs text-sky-400 hover:underline">
          National risk dashboard →
        </Link>
        {loading ? (
          <OperationalSkeleton rows={8} />
        ) : (
          <ul className="space-y-2">
            {(rows as { id: string; name: string; risk_classification: string; counterfeit_vulnerability_score: number }[]).map(
              (m) => (
                <li key={m.id} className="rounded-xl border border-sovereign-800 px-4 py-3 hover:border-sky-500/40">
                  <Link href={`/regulator/medicines/${m.id}`} className="font-medium text-white hover:text-sky-300">
                    {m.name}
                  </Link>
                  <p className="text-xs text-slate-500">
                    {m.risk_classification} · counterfeit vulnerability {m.counterfeit_vulnerability_score}
                  </p>
                </li>
              )
            )}
          </ul>
        )}
      </CommandShell>
    </RegulatorGuard>
  );
}
