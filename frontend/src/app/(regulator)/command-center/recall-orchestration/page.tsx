"use client";

import { useEffect, useState } from "react";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { fetchRecallOrchestration } from "@/services/supply-chain-intelligence";

export default function RecallOrchestrationPage() {
  const [data, setData] = useState<{ campaigns: unknown[]; active_count: number } | null>(null);

  useEffect(() => {
    fetchRecallOrchestration().then((r) => {
      if (r.success && r.data) setData(r.data);
    });
  }, []);

  return (
    <RegulatorGuard>
      <CommandShell
        title="Recall orchestration"
        subtitle="Coordinated national recall campaigns — live API"
      >
        <p className="mb-4 text-sm text-slate-400">{data?.active_count ?? 0} active campaigns</p>
        <ul className="space-y-2">
          {(data?.campaigns as { campaign_code: string; status: string; pharmacies_acknowledged: number; pharmacies_targeted: number }[] ?? []).map(
            (c) => (
              <li key={c.campaign_code} className="rounded-xl border border-rose-500/20 bg-rose-500/5 px-4 py-3">
                <p className="font-medium text-white">{c.campaign_code}</p>
                <p className="text-xs text-slate-500">
                  {c.status} · ack {c.pharmacies_acknowledged}/{c.pharmacies_targeted}
                </p>
              </li>
            )
          )}
        </ul>
      </CommandShell>
    </RegulatorGuard>
  );
}
