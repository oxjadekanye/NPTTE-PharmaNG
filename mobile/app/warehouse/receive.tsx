import { AdvancedScanWorkflow } from "@/components/AdvancedScanWorkflow";
import { EvidenceCapture } from "@/components/EvidenceCapture";
import { ScreenShell } from "@/components/ScreenShell";

export default function WarehouseReceive() {
  return (
    <ScreenShell title="Receive batch">
      <AdvancedScanWorkflow
        title="Warehouse receive"
        scanType="warehouse_receive"
        actorRole="warehouse"
        mode="rapid"
      />
      <EvidenceCapture evidenceType="warehouse_breach" />
    </ScreenShell>
  );
}
