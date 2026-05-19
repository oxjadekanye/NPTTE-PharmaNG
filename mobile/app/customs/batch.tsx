import { AdvancedScanWorkflow } from "@/components/AdvancedScanWorkflow";
import { ScreenShell } from "@/components/ScreenShell";

export default function CustomsBatch() {
  return (
    <ScreenShell title="Import batch">
      <AdvancedScanWorkflow
        title="Batch serial"
        scanType="customs_verify"
        actorRole="customs"
        mode="customs"
      />
    </ScreenShell>
  );
}
