"use client";

import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { CustodyTimeline } from "@/components/custody/CustodyTimeline";
import { GlassPanel } from "@/components/enterprise/GlassPanel";

export default function CustodyLedgerPage() {
  return (
    <RegulatorGuard>
      <CommandShell title="Chain of Custody Ledger">
        <GlassPanel title="Sovereign supply-chain custody" subtitle="Manufacturer → patient timeline">
          <CustodyTimeline />
        </GlassPanel>
      </CommandShell>
    </RegulatorGuard>
  );
}
