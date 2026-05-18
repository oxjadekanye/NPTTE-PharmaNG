"use client";

import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { OperationalPortalTemplate } from "@/components/portals/OperationalPortalTemplate";

export default function DistributorPortalPage() {
  return (
    <RegulatorGuard>
      <OperationalPortalTemplate
        portalId="distributor"
        title="Distributor Operations"
        subtitle="Licensed corridors · diversion controls · wholesale integrity"
        highlights={[
          {
            title: "Licensed territory matrix",
            body: "Geo-fenced sales authorisations with automated breach detection (sim).",
            accent: "sky",
          },
          {
            title: "Abnormal distribution detection",
            body: "Velocity anomalies vs. national baselines with AI risk overlays.",
            accent: "amber",
          },
          {
            title: "Wholesale authentication",
            body: "Batch attestations tied to serialization graph before downstream release.",
            accent: "emerald",
          },
        ]}
      />
    </RegulatorGuard>
  );
}
