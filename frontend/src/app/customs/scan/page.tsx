"use client";

import { MobileScanWorkflow } from "@/components/scanning/MobileScanWorkflow";

export default function CustomsScanPage() {
  return (
    <MobileScanWorkflow
      title="Customs verification"
      subtitle="Import lane scan — verify, hold, or flag suspicious shipments."
      scanType="customs_verify"
      actorRole="customs"
      backHref="/customs"
    />
  );
}
