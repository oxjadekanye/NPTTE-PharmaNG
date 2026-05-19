"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { GlassPanel } from "@/components/enterprise/GlassPanel";
import { CopilotPanel } from "@/components/copilot/CopilotPanel";
import { fetchRegionalIntelligence } from "@/services/command-orchestration";
import { OperationalMap } from "@/components/maps/OperationalMap";

export function RegionalCommandPanel({ regionKey, label }: { regionKey: string; label: string }) {
  const [intel, setIntel] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    fetchRegionalIntelligence(regionKey).then((r) => {
      if (r.success) setIntel(r.data);
    });
  }, [regionKey]);

  return (
    <div className="space-y-4">
      <Link href="/regulator/regions" className="text-xs text-sovereign-accent hover:underline">
        ← All regions
      </Link>
      <GlassPanel title={label} subtitle={`Regional command · ${regionKey}`}>
        {intel ? (
          <ul className="grid gap-2 text-xs text-slate-300 md:grid-cols-2">
            <li>Open investigations: {String(intel.open_investigations)}</li>
            <li>Counterfeit signals: {String(intel.counterfeit_signals)}</li>
            <li>Enforcement readiness: {String(intel.enforcement_readiness)}</li>
            <li>Active officers: {String(intel.active_officers)}</li>
            <li>Overdue tasks: {String(intel.overdue_tasks)}</li>
            <li className="md:col-span-2 text-slate-500">{String(intel.ai_summary_hint)}</li>
          </ul>
        ) : (
          <p className="text-sm text-slate-500">Loading regional intelligence…</p>
        )}
      </GlassPanel>
      <OperationalMap layer="counterfeit" />
      <CopilotPanel contextKey="national_status" compact />
    </div>
  );
}
