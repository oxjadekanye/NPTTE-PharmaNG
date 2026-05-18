"use client";

import { useEffect, useState } from "react";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { OverviewGrid } from "@/components/dashboard/OverviewGrid";
import { AlertTicker } from "@/components/dashboard/AlertTicker";
import { IntelligenceFeed } from "@/components/dashboard/IntelligenceFeed";
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
          },
          {
            label: "Interventions",
            value: String(d.active_interventions ?? "0"),
            numericValue: Number(d.active_interventions) || 0,
            severity: "warning",
          },
          {
            label: "Shortage alerts",
            value: String(e.open_shortage_alerts ?? NATIONAL_KPIS.shortageAlerts),
            numericValue: Number(e.open_shortage_alerts) || NATIONAL_KPIS.shortageAlerts,
            severity: "critical",
          },
          {
            label: "National threat score",
            value: String(d.national_threat ?? "62"),
            numericValue: Number(d.national_threat) || 62,
          },
        ]);
      })
      .catch(() =>
        setMetrics([
          { label: "Shortage alerts", numericValue: NATIONAL_KPIS.shortageAlerts, value: NATIONAL_KPIS.shortageAlerts, severity: "critical" },
          { label: "Fraud alerts", numericValue: NATIONAL_KPIS.fraudAlerts, value: NATIONAL_KPIS.fraudAlerts, severity: "warning" },
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
        <div className="mt-8">
          <IntelligenceFeed />
        </div>
      </CommandShell>
    </RegulatorGuard>
  );
}
