import { AdvancedScanWorkflow } from "@/components/AdvancedScanWorkflow";
import { ScreenShell } from "@/components/ScreenShell";

export default function WarehouseTransfer() {
  return (
    <ScreenShell title="Transfer stock">
      <AdvancedScanWorkflow
        title="Transfer scan"
        scanType="warehouse_receive"
        actorRole="warehouse"
        mode="rapid"
      />
    </ScreenShell>
  );
}
