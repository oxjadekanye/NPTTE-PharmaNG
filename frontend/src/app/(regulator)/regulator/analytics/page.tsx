"use client";

import { useEffect, useState } from "react";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { fetchNationalSummary, fetchMedicineFlow, fetchHeatmaps } from "@/services/command-center";

export default function AnalyticsPage() {
  const [summary, setSummary] = useState<Record<string, unknown>>({});

  useEffect(() => {
    Promise.all([fetchNationalSummary(), fetchMedicineFlow(), fetchHeatmaps()]).then(([s, f, h]) => {
      setSummary({ summary: s.data, flow: f.data, heatmaps: h.data });
    });
  }, []);

  return (
    <RegulatorGuard>
      <CommandShell title="Analytics Intelligence">
        <pre className="overflow-auto rounded-xl border border-sovereign-800 bg-sovereign-950 p-4 text-xs text-slate-400">
          {JSON.stringify(summary, null, 2)}
        </pre>
      </CommandShell>
    </RegulatorGuard>
  );
}
