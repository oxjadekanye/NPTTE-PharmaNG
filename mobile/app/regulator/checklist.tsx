import { InspectionChecklistEngine } from "@/components/InspectionChecklistEngine";
import { ScreenShell } from "@/components/ScreenShell";

export default function RegulatorChecklist() {
  return (
    <ScreenShell title="Inspection checklist" subtitle="Pass/fail sections · compliance score">
      <InspectionChecklistEngine />
    </ScreenShell>
  );
}
