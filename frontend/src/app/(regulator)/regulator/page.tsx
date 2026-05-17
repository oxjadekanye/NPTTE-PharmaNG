"use client";

import { useEffect, useState } from "react";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { OverviewGrid } from "@/components/dashboard/OverviewGrid";
import { useRealtime } from "@/hooks/useRealtime";
import { fetchDashboardOverview, fetchLiveOverview } from "@/services/command-center";
import type { MetricCard } from "@/shared/types";

export default function RegulatorOverviewPage() {
  const [metrics, setMetrics] = useState<MetricCard[]>([]);
  const { connected, messages } = useRealtime(true);

  useEffect(() => {
    Promise.all([fetchLiveOverview(), fetchDashboardOverview()])
      .then(([live, dash]) => {
        const d = { ...dash.data, ...live.data } as Record<string, unknown>;
        const inv = d.inventory as Record<string, unknown> | undefined;
        setMetrics([
          { label: "Open alerts", value: String(d.open_alerts ?? d.open_alerts ?? "—"), severity: "warning" },
          { label: "Fraud flags", value: String(d.unresolved_fraud_flags ?? "—"), severity: "critical" },
          { label: "Verifications (24h)", value: String(d.verification_scans_24h ?? "—") },
          { label: "Open incidents", value: String(d.open_incidents ?? "—"), severity: "warning" },
          { label: "National threat", value: String(d.national_threat ?? "—") },
          { label: "Products tracked", value: String(inv?.total_products ?? "—") },
        ]);
      })
      .catch(() => setMetrics([{ label: "Status", value: "Awaiting API", severity: "warning" }]));
  }, [messages.length]);

  return (
    <RegulatorGuard>
      <CommandShell title="National Overview">
        <div className="mb-4 flex items-center gap-2 text-xs text-slate-500">
          <span className={`h-2 w-2 rounded-full ${connected ? "bg-emerald-500" : "bg-slate-600"}`} />
          Realtime {connected ? "connected" : "polling"}
        </div>
        <OverviewGrid metrics={metrics} />
        <div className="mt-8 rounded-xl border border-amber-500/30 bg-amber-500/5 p-4 text-sm text-amber-200">
          Emergency escalation channel active · Monitor shortages and counterfeit signals nationally.
        </div>
      </CommandShell>
    </RegulatorGuard>
  );
}
