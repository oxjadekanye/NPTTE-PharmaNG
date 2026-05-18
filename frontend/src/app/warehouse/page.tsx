"use client";

import { EnterpriseGuard } from "@/components/shared/EnterpriseGuard";
import { OperationalPortalTemplate } from "@/components/portals/OperationalPortalTemplate";

export default function WarehousePortalPage() {
  return (
    <EnterpriseGuard>
      <OperationalPortalTemplate
        portalId="warehouse"
        title="Warehouse & Logistics Network"
        subtitle="Stock movement · inspections · cold chain · route intelligence"
        highlights={[
          {
            title: "Stock movement & hub orchestration",
            body: "Bond-to-last-mile telemetry with seal integrity checkpoints (simulated).",
            accent: "sky",
          },
          {
            title: "Warehouse inspections",
            body: "Scheduled vs. ad-hoc inspections, findings severity, and remediation timers.",
            accent: "amber",
          },
          {
            title: "Temperature breach alerts",
            body: "Lane-level cold-chain deviation with automatic regulator notification stubs.",
            accent: "rose",
          },
          {
            title: "Logistics verification",
            body: "Manifest cross-check against serialization graph and customs release states.",
            accent: "emerald",
          },
        ]}
      />
    </EnterpriseGuard>
  );
}
