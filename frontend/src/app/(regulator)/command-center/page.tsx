"use client";

import { useEffect, useState } from "react";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { OverviewGrid } from "@/components/dashboard/OverviewGrid";
import { fetchLiveOverview, fetchEmergencyResponse } from "@/services/command-center";
import type { MetricCard } from "@/shared/types";

export default function CommandCenterPage() {
  const [metrics, setMetrics] = useState<MetricCard[]>([]);

  useEffect(() => {
    Promise.all([fetchLiveOverview(), fetchEmergencyResponse()]).then(([live, emergency]) => {
      const d = live.data as Record<string, unknown>;
      const e = emergency.data as Record<string, unknown>;
      setMetrics([
        { label: "Active disruptions", value: String(d.active_disruptions ?? "0") },
        { label: "Interventions", value: String(d.active_interventions ?? "0"), severity: "warning" },
        { label: "Shortage alerts", value: String(e.open_shortage_alerts ?? "0"), severity: "critical" },
        { label: "Threat score", value: String(d.national_threat ?? "0") },
      ]);
    });
  }, []);

  return (
    <RegulatorGuard>
      <CommandShell title="National Command Center">
        <OverviewGrid metrics={metrics} />
      </CommandShell>
    </RegulatorGuard>
  );
}
