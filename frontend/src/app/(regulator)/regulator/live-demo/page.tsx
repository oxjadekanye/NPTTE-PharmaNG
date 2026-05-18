"use client";

import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { TraceabilityLiveDemo } from "@/components/demo/TraceabilityLiveDemo";

export default function RegulatorLiveDemoPage() {
  return (
    <RegulatorGuard>
      <CommandShell title="Live traceability demo">
        <p className="mb-6 max-w-2xl text-sm text-slate-500">
          End-to-end national journey — manufacturer serialization through pharmacy to citizen
          verification. All records tagged{" "}
          <code className="text-sovereign-accent">metadata.demo_type = traceability_demo</code>.
        </p>
        <TraceabilityLiveDemo />
      </CommandShell>
    </RegulatorGuard>
  );
}
