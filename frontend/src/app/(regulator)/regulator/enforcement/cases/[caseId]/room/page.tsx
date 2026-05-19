"use client";

import { useParams } from "next/navigation";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { InvestigationRoomPanel } from "@/components/investigation/InvestigationRoomPanel";

export default function InvestigationRoomPage() {
  const params = useParams<{ caseId: string }>();
  const caseId = decodeURIComponent(params.caseId ?? "");

  return (
    <RegulatorGuard>
      <CommandShell title="Investigation room">
        <InvestigationRoomPanel caseId={caseId} />
      </CommandShell>
    </RegulatorGuard>
  );
}
