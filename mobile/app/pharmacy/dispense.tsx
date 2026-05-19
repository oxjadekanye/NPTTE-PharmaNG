import { AdvancedScanWorkflow } from "@/components/AdvancedScanWorkflow";
import { ScreenShell } from "@/components/ScreenShell";

export default function PharmacyDispense() {
  return (
    <ScreenShell title="Dispense">
      <AdvancedScanWorkflow title="Dispense serial" scanType="pharmacy_dispense" actorRole="pharmacy" />
    </ScreenShell>
  );
}
