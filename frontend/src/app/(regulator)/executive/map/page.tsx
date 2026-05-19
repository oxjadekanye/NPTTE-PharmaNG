"use client";

import Link from "next/link";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { OperationalMap } from "@/components/maps/OperationalMap";
import { ExecutiveAiBriefingPanel } from "@/components/copilot/ExecutiveAiBriefingPanel";

export default function ExecutiveMapPage() {
  return (
    <RegulatorGuard>
      <CommandShell title="Executive · National map">
        <Link href="/executive" className="text-xs text-sovereign-accent hover:underline">
          ← Executive mode
        </Link>
        <div className="mt-4 space-y-6">
          <OperationalMap layer="counterfeit" />
          <ExecutiveAiBriefingPanel compact />
        </div>
      </CommandShell>
    </RegulatorGuard>
  );
}
