"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { GlassPanel } from "@/components/enterprise/GlassPanel";
import { fetchExecutiveBriefing, fetchNarratives } from "@/services/sovereign-intelligence";

export default function IntelligenceNarrativesPage() {
  const [narratives, setNarratives] = useState<Record<string, unknown>[]>([]);
  const [briefing, setBriefing] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    fetchNarratives().then((r) => setNarratives((r.data?.narratives as Record<string, unknown>[]) ?? []));
    fetchExecutiveBriefing().then((r) => setBriefing(r.data ?? null));
  }, []);

  return (
    <RegulatorGuard>
      <CommandShell title="Intelligence narratives">
        <Link href="/regulator/intelligence" className="text-xs text-sovereign-accent">
          ← Intelligence
        </Link>
        {briefing && (
          <GlassPanel title="Ministerial briefing" subtitle="Phase 18 executive briefing" accent="amber" className="mt-6">
            <p className="text-xs text-slate-300 whitespace-pre-wrap">{String(briefing.ministerial_briefing)}</p>
            <div className="mt-4 grid grid-cols-2 gap-2 text-xs text-slate-500 md:grid-cols-3">
              <p>Stability index: {String(briefing.medicine_stability_index)}</p>
              <p>Counterfeit forecast: {String(briefing.counterfeit_risk_forecast)}</p>
              <p>Enforcement readiness: {String(briefing.enforcement_readiness_score)}</p>
            </div>
          </GlassPanel>
        )}
        <div className="mt-6 space-y-4">
          {narratives.map((n) => (
            <GlassPanel key={String(n.id)} title={String(n.title)} subtitle={String(n.narrative_type)}>
              <p className="text-xs text-slate-300 whitespace-pre-wrap">{String(n.body)}</p>
            </GlassPanel>
          ))}
          {narratives.length === 0 && <p className="text-sm text-slate-500">No narratives yet. Run national risk refresh.</p>}
        </div>
      </CommandShell>
    </RegulatorGuard>
  );
}
