import { AdvancedScanWorkflow } from "@/components/AdvancedScanWorkflow";
import { EvidenceCapture } from "@/components/EvidenceCapture";
import { ScreenShell } from "@/components/ScreenShell";

export default function RegulatorInspect() {
  return (
    <ScreenShell title="Field inspection">
      <AdvancedScanWorkflow
        title="Inspect product"
        scanType="regulator_inspection"
        actorRole="regulator"
        mode="inspection"
      />
      <EvidenceCapture evidenceType="inspection" />
    </ScreenShell>
  );
}
