"use client";

import { MobileScanWorkflow } from "@/components/scanning/MobileScanWorkflow";

export default function CitizenScanPage() {
  return (
    <MobileScanWorkflow
      title="Citizen medicine scan"
      subtitle="Verify authenticity before use. Works offline — scans sync when connectivity returns."
      scanType="citizen_verify"
      actorRole="citizen"
      requireAuth={false}
      backHref="/citizen"
    />
  );
}
