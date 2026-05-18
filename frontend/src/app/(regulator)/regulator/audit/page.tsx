"use client";

import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { AuditPanel } from "@/components/audit/AuditPanel";

export default function AuditPage() {
  return (
    <RegulatorGuard>
      <CommandShell title="Audit & Security">
        <AuditPanel />
      </CommandShell>
    </RegulatorGuard>
  );
}
