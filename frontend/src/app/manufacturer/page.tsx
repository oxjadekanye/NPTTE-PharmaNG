"use client";

import { EnterpriseGuard } from "@/components/shared/EnterpriseGuard";
import { OperationalPortalTemplate } from "@/components/portals/OperationalPortalTemplate";

export default function ManufacturerPortalPage() {
  return (
    <EnterpriseGuard>
      <OperationalPortalTemplate
        portalId="manufacturer"
        title="Manufacturer Operations"
        subtitle="Batch production · serialization · regulatory communications · export integrity"
        highlights={[
          {
            title: "Company profile & regulatory status",
            body: "GMP licence matrix, inspection readiness, and NAFDAC correspondence queue (simulated).",
            accent: "sky",
          },
          {
            title: "Product catalogue & registration",
            body: "SKU lifecycle, dossier milestones, and conditional approvals tracked in sovereign registry.",
            accent: "emerald",
          },
          {
            title: "Batch production & COA upload",
            body: "Line-level batch issuance, certificate of analysis vault, and deviation alerts.",
            accent: "amber",
          },
          {
            title: "Serialization approval queue",
            body: "Serial ranges pending regulator sign-off with immutable issuance timelines.",
            accent: "sky",
          },
          {
            title: "Manufacturing line simulation",
            body: "Active line throughput, changeover windows, and OEE-style indicators for national reporting.",
            accent: "emerald",
          },
          {
            title: "Export tracking & compliance scoring",
            body: "Destination markets, cold-chain attestations, and composite compliance index vs. peers.",
            accent: "rose",
          },
        ]}
      />
    </EnterpriseGuard>
  );
}
