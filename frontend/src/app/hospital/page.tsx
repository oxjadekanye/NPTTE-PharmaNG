"use client";

import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { OperationalPortalTemplate } from "@/components/portals/OperationalPortalTemplate";

export default function HospitalPortalPage() {
  return (
    <RegulatorGuard>
      <OperationalPortalTemplate
        portalId="hospital"
        title="Hospital Pharmacy & Therapeutics"
        subtitle="Formulary · high-risk meds · adverse signal intake"
        highlights={[
          {
            title: "Formulary & procurement alignment",
            body: "National essential medicines list sync with shortage-aware substitution rules.",
            accent: "sky",
          },
          {
            title: "Ward-level verification",
            body: "Bedside scan hooks for high-value ARV/oncology lines (UI simulation).",
            accent: "emerald",
          },
          {
            title: "Adverse reaction triage",
            body: "Signals routed to pharmacovigilance desk with incident correlation stubs.",
            accent: "rose",
          },
        ]}
      />
    </RegulatorGuard>
  );
}
