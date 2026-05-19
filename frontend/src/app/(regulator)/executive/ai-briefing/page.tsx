"use client";

import Link from "next/link";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { ExecutiveAiBriefingPanel } from "@/components/copilot/ExecutiveAiBriefingPanel";

export default function ExecutiveAiBriefingPage() {
  return (
    <RegulatorGuard>
      <CommandShell title="Executive · AI Briefing">
        <Link href="/executive" className="text-xs text-sovereign-accent hover:underline">
          ← Executive mode
        </Link>
        <div className="mt-6">
          <ExecutiveAiBriefingPanel />
        </div>
      </CommandShell>
    </RegulatorGuard>
  );
}
