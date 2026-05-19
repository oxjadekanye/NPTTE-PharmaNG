"use client";

import { useEffect, useState } from "react";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { OverviewGrid } from "@/components/dashboard/OverviewGrid";
import { NationalStatusBanner } from "@/components/dashboard/NationalStatusBanner";
import { IntelligenceFeed } from "@/components/dashboard/IntelligenceFeed";
import { AlertTicker } from "@/components/dashboard/AlertTicker";
import { ActivityLog } from "@/components/dashboard/ActivityLog";
import { MinisterialOverview } from "@/components/dashboard/MinisterialOverview";
import { DemoEnvironmentPanel } from "@/components/dashboard/DemoEnvironmentPanel";
import { IntelligenceHighlights } from "@/components/dashboard/IntelligenceHighlights";
import { useRealtime } from "@/hooks/useRealtime";
import { useSimulatedRealtime } from "@/hooks/useSimulatedRealtime";
import { useCommandStore } from "@/store/command-store";
import { fetchDashboardOverview, fetchLiveOverview } from "@/services/command-center";
import { NATIONAL_KPIS } from "@/demo/nigeria-intelligence";
import type { MetricCard } from "@/shared/types";

function buildMetrics(api: Record<string, unknown>): MetricCard[] {
  const inv = api.inventory as Record<string, unknown> | undefined;
  const openAlerts = Number(api.open_alerts) || 0;
  const fraud = Number(api.unresolved_fraud_flags) || NATIONAL_KPIS.fraudAlerts;
  const scans = Number(api.verification_scans_24h) || NATIONAL_KPIS.verificationsToday;
  const incidents = Number(api.open_incidents) || NATIONAL_KPIS.activeInvestigations;
  const ex = (t: string, id: string) => ({ entityType: t, entityId: id });

  return [
    {
      label: "Verifications (24h)",
      value: scans,
      numericValue: scans,
      pulse: true,
      explorer: ex("national_risk", "national-risk-current"),
    },
    {
      label: "Counterfeit detections",
      value: NATIONAL_KPIS.counterfeitDetections,
      numericValue: NATIONAL_KPIS.counterfeitDetections,
      severity: "critical",
      pulse: true,
      explorer: ex("national_risk", "counterfeit-detections-current"),
    },
    {
      label: "Open alerts",
      value: openAlerts || "—",
      numericValue: openAlerts || undefined,
      severity: "warning",
      explorer: ex("alert", "open-alerts-current"),
    },
    {
      label: "Fraud flags",
      value: fraud,
      numericValue: fraud,
      severity: "critical",
      explorer: ex("national_risk", "fraud-flags-current"),
    },
    {
      label: "Active investigations",
      value: incidents,
      numericValue: incidents,
      severity: "warning",
      explorer: ex("national_risk", "active-investigations-current"),
    },
    {
      label: "Products tracked",
      value: String(inv?.total_products ?? "12,400+"),
      numericValue: Number(inv?.total_products) || 12400,
      explorer: ex("product", "products-tracked-current"),
    },
  ];
}

export default function RegulatorOverviewPage() {
  const [metrics, setMetrics] = useState<MetricCard[]>([]);
  const [loading, setLoading] = useState(true);
  const mode = useCommandStore((s) => s.mode);
  const { connected } = useRealtime(true);
  useSimulatedRealtime(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([fetchLiveOverview(), fetchDashboardOverview()])
      .then(([live, dash]) => {
        const d = { ...dash.data, ...live.data } as Record<string, unknown>;
        setMetrics(buildMetrics(d));
      })
      .catch(() => setMetrics(buildMetrics({})))
      .finally(() => setLoading(false));
  }, []);

  return (
    <RegulatorGuard>
      <CommandShell title="National Overview">
        <div className="mb-4 flex flex-wrap items-center gap-3 text-xs text-slate-500">
          <span className={`h-2 w-2 rounded-full ${connected ? "bg-emerald-500" : "bg-slate-600"}`} />
          Realtime {connected ? "SSE connected" : "simulated feed active"}
        </div>

        {mode === "ministerial" ? (
          <MinisterialOverview />
        ) : (
          <div className="space-y-6">
            <NationalStatusBanner />
            <AlertTicker />
            {loading ? (
              <p className="text-sm text-slate-500">Loading national metrics…</p>
            ) : (
              <OverviewGrid metrics={metrics} />
            )}
            <IntelligenceHighlights />
            <div className="grid gap-6 xl:grid-cols-3">
              <div className="xl:col-span-2">
                <IntelligenceFeed />
              </div>
              <ActivityLog />
            </div>
            <DemoEnvironmentPanel />
          </div>
        )}
      </CommandShell>
    </RegulatorGuard>
  );
}
