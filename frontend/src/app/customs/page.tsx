"use client";

import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { OperationalPortalTemplate } from "@/components/portals/OperationalPortalTemplate";

export default function CustomsPortalPage() {
  return (
    <RegulatorGuard>
      <OperationalPortalTemplate
        portalId="customs"
        title="Customs Intelligence"
        subtitle="Import manifests · seizures · border authentication · watchlists"
        highlights={[
          {
            title: "Import manifest monitoring",
            body: "Risk-scored pharmaceutical lanes with secondary inspection queues.",
            accent: "sky",
          },
          {
            title: "Seized medication registry",
            body: "Chain-of-custody from seizure through laboratory referral and destruction scheduling.",
            accent: "rose",
          },
          {
            title: "Suspicious import scoring",
            body: "AI-simulated composite score blending origin, carrier, and documentation entropy.",
            accent: "amber",
          },
          {
            title: "International watchlists",
            body: "Cross-reference with INTERPOL-style stubs and domestic regulator blacklists.",
            accent: "emerald",
          },
        ]}
      />
    </RegulatorGuard>
  );
}
