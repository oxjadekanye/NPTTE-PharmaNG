"use client";

import { useEffect, useState } from "react";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { fetchManufacturerIntelligence } from "@/services/medicine-intelligence";

export default function ManufacturerIntelligencePage() {
  const [rows, setRows] = useState<unknown[]>([]);

  useEffect(() => {
    fetchManufacturerIntelligence().then((r) => setRows(r.data?.manufacturers ?? []));
  }, []);

  return (
    <RegulatorGuard>
      <CommandShell title="Manufacturer intelligence" subtitle="National manufacturing risk indicators">
        <ul className="space-y-2">
          {(rows as { id: string; name: string; compliance_score: number; suspicious_manufacturer_indicator: boolean }[]).map(
            (m) => (
              <li key={m.id} className="rounded-lg border border-sovereign-800 px-4 py-3 text-sm">
                <span className="font-medium text-white">{m.name}</span>
                <span className="ml-2 text-slate-500">
                  score {m.compliance_score}
                  {m.suspicious_manufacturer_indicator && " · flagged"}
                </span>
              </li>
            )
          )}
        </ul>
      </CommandShell>
    </RegulatorGuard>
  );
}
