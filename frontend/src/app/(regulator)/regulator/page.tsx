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
  return [
    {
      label: "Verifications (24h)",
      value: scans,
      numericValue: scans,
      pulse: true,
      explorerContext: "verifications_24h",
    },
    {
      label: "Counterfeit detections",
      value: NATIONAL_KPIS.counterfeitDetections,
      numericValue: NATIONAL_KPIS.counterfeitDetections,
      severity: "critical",
      pulse: true,
      explorerContext: "counterfeit_detections",
    },
    {
      label: "Open alerts",
      value: openAlerts || "—",
      numericValue: openAlerts || undefined,
      severity: "warning",
      explorerContext: "open_alerts",
    },
    {
      label: "Fraud flags",
      value: fraud,
      numericValue: fraud,
      severity: "critical",
      explorerContext: "fraud_flags",
    },
    {
      label: "Active investigations",
      value: incidents,
      numericValue: incidents,
      severity: "warning",
      explorerContext: "active_investigations",
    },
    {
      label: "Products tracked",
      value: String(inv?.total_products ?? "12,400+"),
      numericValue: Number(inv?.total_products) || 12400,
      explorerContext: "products_tracked",
    },
  ];
}

export default function RegulatorOverviewPage() {
  const [metrics, setMetrics] = useState<MetricCard[]>(() => buildMetrics({}));
  const [refreshing, setRefreshing] = useState(false);
  const mode = useCommandStore((s) => s.mode);
  const { connected } = useRealtime(true);
  useSimulatedRealtime(true);

  useEffect(() => {
    setRefreshing(true);
    Promise.allSettled([fetchLiveOverview(), fetchDashboardOverview()]).then((results) => {
      const live = results[0].status === "fulfilled" ? results[0].value : null;
      const dash = results[1].status === "fulfilled" ? results[1].value : null;
      const d = {
        ...(dash?.data ?? {}),
        ...(live?.data ?? {}),
      } as Record<string, unknown>;
      setMetrics(buildMetrics(d));
      setRefreshing(false);
    });
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
            <OverviewGrid metrics={metrics} />
            {refreshing && (
              <p className="text-[10px] text-slate-600">Refreshing national metrics…</p>
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
