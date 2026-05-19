import { AdvancedScanWorkflow } from "@/components/AdvancedScanWorkflow";
import { ScreenShell } from "@/components/ScreenShell";

export default function PharmacyReceive() {
  return (
    <ScreenShell title="Receive stock">
      <AdvancedScanWorkflow title="Receive serial" scanType="pharmacy_receive" actorRole="pharmacy" />
    </ScreenShell>
  );
}
