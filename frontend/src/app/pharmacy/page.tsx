"use client";

import { EnterpriseGuard } from "@/components/shared/EnterpriseGuard";
import { OperationalPortalTemplate } from "@/components/portals/OperationalPortalTemplate";

export default function PharmacyPortalPage() {
  return (
    <EnterpriseGuard>
      <OperationalPortalTemplate
        portalId="pharmacy"
        title="Pharmacy Operations"
        subtitle="Inventory · dispense · traceability scanner · shortage & counterfeit vigilance"
        highlights={[
          {
            title: "Inventory center & receive batches",
            body: "Lot receipts, custody scans, and quarantine lanes with temperature excursion hooks.",
            accent: "sky",
          },
          {
            title: "Dispense workflow",
            body: "Serial-first dispensing, patient verification lookup, and audit-ready transaction logs.",
            accent: "emerald",
          },
          {
            title: "Traceability scanner",
            body: "Handheld and counter modes with duplicate-scan and diversion pattern detection.",
            accent: "amber",
          },
          {
            title: "Suspicious medication & recall notifications",
            body: "National recall propagation with acknowledgement SLA and escalation to PCN.",
            accent: "rose",
          },
          {
            title: "Shortage monitor",
            body: "SKU-level cover hours, substitution policy hints, and cross-state redistribution signals.",
            accent: "sky",
          },
          {
            title: "Compliance monitoring",
            body: "Dispense-to-receive ratios, after-hours anomaly scoring, and staff attestation trails.",
            accent: "emerald",
          },
        ]}
      />
    </EnterpriseGuard>
  );
}
