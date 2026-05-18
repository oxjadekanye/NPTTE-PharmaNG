"use client";

import { MobileScanWorkflow } from "@/components/scanning/MobileScanWorkflow";

export default function WarehouseScanPage() {
  return (
    <MobileScanWorkflow
      title="Warehouse receiving"
      subtitle="Inbound scan with cold-chain breach detection on suspicious reads."
      scanType="warehouse_receive"
      actorRole="warehouse"
      backHref="/warehouse"
    />
  );
}
