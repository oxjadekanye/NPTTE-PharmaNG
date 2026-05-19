import { EvidenceCapture } from "@/components/EvidenceCapture";
import { ScreenShell } from "@/components/ScreenShell";

export default function RegulatorEvidence() {
  return (
    <ScreenShell title="Evidence capture" subtitle="Photo · GPS · offline queue">
      <EvidenceCapture evidenceType="inspection" />
    </ScreenShell>
  );
}
