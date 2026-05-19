"use client";

import { useEffect, useState } from "react";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { OverviewGrid } from "@/components/dashboard/OverviewGrid";
import { AlertTicker } from "@/components/dashboard/AlertTicker";
import { IntelligenceFeed } from "@/components/dashboard/IntelligenceFeed";
import { LiveEventFeed } from "@/components/realtime/LiveEventFeed";
import { fetchLiveOverview, fetchEmergencyResponse } from "@/services/command-center";
import { useSimulatedRealtime } from "@/hooks/useSimulatedRealtime";
import { NATIONAL_KPIS } from "@/demo/nigeria-intelligence";
import type { MetricCard } from "@/shared/types";

export default function CommandCenterPage() {
  const [metrics, setMetrics] = useState<MetricCard[]>([]);
  useSimulatedRealtime(true);

  useEffect(() => {
    Promise.all([fetchLiveOverview(), fetchEmergencyResponse()])
      .then(([live, emergency]) => {
        const d = live.data as Record<string, unknown>;
        const e = emergency.data as Record<string, unknown>;
        setMetrics([
          {
            label: "Active disruptions",
            value: String(d.active_disruptions ?? "0"),
            numericValue: Number(d.active_disruptions) || 0,
            pulse: true,
            explorer: { entityType: "national_risk", entityId: "high-risk-current" },
          },
          {
            label: "Interventions",
            value: String(d.active_interventions ?? "0"),
            numericValue: Number(d.active_interventions) || 0,
            severity: "warning",
            explorer: { entityType: "national_risk", entityId: "active-investigations-current" },
          },
          {
            label: "Shortage alerts",
            value: String(e.open_shortage_alerts ?? NATIONAL_KPIS.shortageAlerts),
            numericValue: Number(e.open_shortage_alerts) || NATIONAL_KPIS.shortageAlerts,
            severity: "critical",
            explorer: { entityType: "national_risk", entityId: "national-risk-current" },
          },
          {
            label: "National threat score",
            value: String(d.national_threat ?? "62"),
            numericValue: Number(d.national_threat) || 62,
            explorer: { entityType: "national_risk", entityId: "national-risk-current" },
          },
        ]);
      })
      .catch(() =>
        setMetrics([
          { label: "Shortage alerts", numericValue: NATIONAL_KPIS.shortageAlerts, value: NATIONAL_KPIS.shortageAlerts, severity: "critical", explorer: { entityType: "national_risk", entityId: "national-risk-current" } },
          { label: "Fraud alerts", numericValue: NATIONAL_KPIS.fraudAlerts, value: NATIONAL_KPIS.fraudAlerts, severity: "warning", explorer: { entityType: "national_risk", entityId: "fraud-flags-current" } },
        ])
      );
  }, []);

  return (
    <RegulatorGuard>
      <CommandShell title="National Command Center">
        <AlertTicker />
        <div className="mt-6">
          <OverviewGrid metrics={metrics} />
        </div>
        <div className="mt-8 grid gap-6 lg:grid-cols-2">
          <LiveEventFeed />
          <IntelligenceFeed />
        </div>
      </CommandShell>
    </RegulatorGuard>
  );
}
