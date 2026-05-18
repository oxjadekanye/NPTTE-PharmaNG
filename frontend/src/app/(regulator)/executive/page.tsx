"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { useIntelligenceBusStore } from "@/store/intelligence-bus-store";
import { fetchNationalOperationsSummary } from "@/services/national-operations";
import { fetchExecutiveBriefing, fetchNationalIntelligence } from "@/services/sovereign-intelligence";
import type { NationalOperationsSummary } from "@/services/national-operations";
import { GlassPanel } from "@/components/enterprise/GlassPanel";

const MinisterialOverview = dynamic(
  () => import("@/components/dashboard/MinisterialOverview").then((m) => m.MinisterialOverview),
  {
    ssr: false,
    loading: () => (
      <div className="flex min-h-[200px] items-center justify-center rounded-xl border border-sovereign-800 bg-sovereign-900 text-slate-500">
        Loading ministerial intelligence…
      </div>
    ),
  }
);

export default function ExecutiveModePage() {
  const nationalThreatIndex = useIntelligenceBusStore((s) => s.nationalThreatIndex);
  const [summary, setSummary] = useState<NationalOperationsSummary | null>(null);
  const [summaryError, setSummaryError] = useState<string | null>(null);
  const [aiIntel, setAiIntel] = useState<Record<string, unknown> | null>(null);
  const [briefing, setBriefing] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchNationalIntelligence()
      .then((r) => !cancelled && r.success && setAiIntel(r.data))
      .catch(() => setAiIntel(null));
    fetchExecutiveBriefing()
      .then((r) => !cancelled && r.success && setBriefing(r.data))
      .catch(() => setBriefing(null));
    fetchNationalOperationsSummary()
      .then((r) => {
        if (!cancelled && r.success) setSummary(r.data);
      })
      .catch(() => {
        if (!cancelled) setSummaryError("Connect to API for live national summary (regulator JWT).");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <RegulatorGuard>
      <CommandShell title="Executive · Ministerial Command">
        <div className="space-y-6">
          <div className="grid gap-4 lg:grid-cols-3">
            <GlassPanel title="Live national threat composite" subtitle="Intelligence bus (client simulation)">
              <p className="text-4xl font-semibold tabular-nums text-white">{nationalThreatIndex}</p>
              <p className="mt-2 text-xs text-slate-500">
                Counterfeit trends, customs seizures, import dependency, and shortage forecasts synthesised for
                leadership briefings.
              </p>
            </GlassPanel>
            <GlassPanel title="API snapshot" subtitle="GET /api/v1/events/national-summary/" accent="emerald">
              {summaryError && <p className="text-sm text-amber-300">{summaryError}</p>}
              {summary && (
                <ul className="space-y-1 text-xs text-slate-300">
                  <li>Threat index (server): {summary.national_threat_index}</li>
                  <li>Verifications (24h roll): {summary.verifications_24h_roll.toLocaleString()}</li>
                  <li>Customs holds: {summary.customs_holds_open}</li>
                  <li>Shortage watch: {summary.shortage_watch_states.join(", ")}</li>
                  <li className="text-slate-600">Generated {summary.generated_at}</li>
                </ul>
              )}
              {!summary && !summaryError && <p className="text-sm text-slate-500">Loading…</p>}
            </GlassPanel>
            <GlassPanel title="National AI intelligence (Phase 10)" accent="amber">
              {aiIntel ? (
                <ul className="space-y-1 text-xs text-slate-300">
                  <li>National risk: {String(aiIntel.national_risk_score)}</li>
                  <li>Shortage forecast: {String(aiIntel.shortage_forecast_probability)}%</li>
                  <li>Diversion risk: {String(aiIntel.diversion_risk_probability)}%</li>
                  <li>Counterfeit signals: {String(aiIntel.counterfeit_signals_24h)}</li>
                </ul>
              ) : (
                <p className="text-sm text-slate-400">Loading /intelligence/national/ …</p>
              )}
            </GlassPanel>
          </div>
          {briefing && (
            <GlassPanel title="Phase 18 sovereign briefing" subtitle="Deterministic ministerial narrative" accent="rose">
              <div className="grid gap-3 text-xs text-slate-300 md:grid-cols-3">
                <p>Medicine stability index: {String(briefing.medicine_stability_index)}</p>
                <p>Counterfeit risk forecast: {String(briefing.counterfeit_risk_forecast)}</p>
                <p>Shortage pressure: {String(briefing.shortage_pressure)}</p>
                <p>Import disruption: {String(briefing.import_disruption_indicator)}</p>
                <p>Enforcement readiness: {String(briefing.enforcement_readiness_score)}</p>
              </div>
              <p className="mt-4 text-sm text-slate-200 whitespace-pre-wrap">{String(briefing.ministerial_briefing)}</p>
            </GlassPanel>
          )}
          <MinisterialOverview />
        </div>
      </CommandShell>
    </RegulatorGuard>
  );
}
