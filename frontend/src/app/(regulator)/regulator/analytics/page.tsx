"use client";

import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { AnalyticsDashboard } from "@/components/analytics/AnalyticsDashboard";
import { useSimulatedRealtime } from "@/hooks/useSimulatedRealtime";

export default function AnalyticsPage() {
  useSimulatedRealtime(true);

  return (
    <RegulatorGuard>
      <CommandShell title="Analytics Intelligence">
        <AnalyticsDashboard />
      </CommandShell>
    </RegulatorGuard>
  );
}
