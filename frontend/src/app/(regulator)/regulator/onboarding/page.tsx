"use client";

import { useEffect, useState } from "react";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { GlassPanel } from "@/components/enterprise/GlassPanel";
import { fetchOnboardingWorkflows } from "@/services/pilot-readiness";

export default function OnboardingWorkflowsPage() {
  const [workflows, setWorkflows] = useState<unknown[]>([]);

  useEffect(() => {
    fetchOnboardingWorkflows()
      .then((r) => r.success && setWorkflows(r.data.workflows ?? []))
      .catch(() => setWorkflows([]));
  }, []);

  return (
    <RegulatorGuard>
      <CommandShell title="Real Data Onboarding">
        <p className="mb-6 text-sm text-slate-500">
          Manufacturer · distributor · pharmacy · warehouse · hospital · regulator user workflows
        </p>
        <div className="grid gap-4 xl:grid-cols-2">
          {workflows.map((w, i) => (
            <GlassPanel key={i} title={String((w as { label?: string }).label ?? "Workflow")}>
              <pre className="max-h-64 overflow-auto text-[10px] text-slate-400">{JSON.stringify(w, null, 2)}</pre>
            </GlassPanel>
          ))}
        </div>
      </CommandShell>
    </RegulatorGuard>
  );
}
