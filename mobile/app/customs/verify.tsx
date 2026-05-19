import { AdvancedScanWorkflow } from "@/components/AdvancedScanWorkflow";
import { EvidenceCapture } from "@/components/EvidenceCapture";
import { ScreenShell } from "@/components/ScreenShell";

export default function CustomsVerify() {
  return (
    <ScreenShell title="Verify shipment">
      <AdvancedScanWorkflow
        title="Customs verify"
        scanType="customs_verify"
        actorRole="customs"
        mode="customs"
      />
      <EvidenceCapture evidenceType="customs_seizure" />
    </ScreenShell>
  );
}
