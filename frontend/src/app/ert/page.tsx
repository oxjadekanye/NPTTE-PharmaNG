"use client";

import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { OperationalPortalTemplate } from "@/components/portals/OperationalPortalTemplate";

export default function EmergencyResponseTeamsPage() {
  return (
    <RegulatorGuard>
      <OperationalPortalTemplate
        portalId="ert"
        title="Emergency Response Teams"
        subtitle="Readiness · mobilisation · cross-agency playbooks"
        highlights={[
          {
            title: "National readiness index",
            body: "Stockpile depth, transport assets, and regulator liaison activation windows.",
            accent: "emerald",
          },
          {
            title: "Mobilisation workflows",
            body: "Scenario templates for pandemic surge, port disruption, and recall acceleration.",
            accent: "sky",
          },
          {
            title: "Inter-agency collaboration",
            body: "Shared incident rooms with customs, NDLEA, and state health commands (sim).",
            accent: "amber",
          },
        ]}
      />
    </RegulatorGuard>
  );
}
