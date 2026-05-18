"use client";

import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { PilotReadinessDashboard } from "@/components/pilot/PilotReadinessDashboard";

export default function PilotReadinessPage() {
  return (
    <RegulatorGuard>
      <CommandShell title="Pilot Readiness">
        <PilotReadinessDashboard />
      </CommandShell>
    </RegulatorGuard>
  );
}
