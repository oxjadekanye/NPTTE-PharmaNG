import { ScanWorkflow } from "@/components/ScanWorkflow";
import { ScreenShell } from "@/components/ScreenShell";

export default function CitizenScan() {
  return (
    <ScreenShell title="Verify product" subtitle="Uses POST /scanning/ingest/ (citizen_verify)">
      <ScanWorkflow title="Scan medicine" scanType="citizen_verify" actorRole="citizen" />
    </ScreenShell>
  );
}
