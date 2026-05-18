"use client";

import { useEffect, useMemo } from "react";
import { EnterprisePortalShell } from "@/components/portals/EnterprisePortalShell";
import { ECOSYSTEM_HUB_NAV } from "@/config/portal-nav";
import { useIntelligenceBusStore, randomSimulatedBusEvent } from "@/store/intelligence-bus-store";
import { computePortalRiskScores } from "@/intelligence/ai-risk-simulation";
import { RiskScoreStrip } from "@/components/enterprise/RiskScoreStrip";
import { GlassPanel } from "@/components/enterprise/GlassPanel";
import { NATIONAL_KPIS, ACTIVE_RECALLS, INITIAL_FEED } from "@/demo/nigeria-intelligence";

export function OperationalPortalTemplate({
  portalId,
  title,
  subtitle,
  highlights,
}: {
  portalId: string;
  title: string;
  subtitle: string;
  highlights: { title: string; body: string; accent?: "emerald" | "sky" | "amber" | "rose" }[];
}) {
  const push = useIntelligenceBusStore((s) => s.push);
  const bus = useIntelligenceBusStore((s) => s.bus);
  const nationalThreatIndex = useIntelligenceBusStore((s) => s.nationalThreatIndex);

  useEffect(() => {
    const t = setInterval(() => {
      push(randomSimulatedBusEvent());
    }, 11000);
    return () => clearInterval(t);
  }, [push]);

  const scores = useMemo(() => computePortalRiskScores(portalId), [portalId]);
  const feed = useMemo(() => [...bus.slice(0, 8), ...INITIAL_FEED.slice(0, 4)], [bus]);

  return (
    <EnterprisePortalShell title={title} subtitle={subtitle} nav={ECOSYSTEM_HUB_NAV}>
      <div className="space-y-6">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Metric label="National threat index" value={nationalThreatIndex} suffix="" pulse />
          <Metric label="24h verifications (sim)" value={NATIONAL_KPIS.verificationsToday} suffix="" />
          <Metric label="Active recalls" value={NATIONAL_KPIS.recallsActive} suffix="" />
          <Metric label="Compliance rate" value={NATIONAL_KPIS.complianceRate} suffix="%" />
        </div>

        <RiskScoreStrip scores={scores.slice(0, 5)} />

        <div className="grid gap-6 lg:grid-cols-3">
          <GlassPanel className="lg:col-span-2" title="Operational workspace" subtitle="Live intelligence bus (simulated)">
            <ul className="max-h-80 space-y-2 overflow-y-auto text-sm">
              {feed.map((e, idx) => (
                <li
                  key={`${e.id}-${idx}`}
                  className="flex gap-3 rounded-lg border border-sovereign-800/80 bg-sovereign-950/40 px-3 py-2"
                >
                  <span className="shrink-0 font-mono text-[10px] text-sovereign-accent">
                    {(e as { channel?: string }).channel ?? e.type}
                  </span>
                  <span className="text-slate-300">{e.message}</span>
                </li>
              ))}
            </ul>
          </GlassPanel>
          <GlassPanel title="Active recalls (DEMO)" subtitle="National propagation monitor">
            <ul className="space-y-2 text-sm">
              {ACTIVE_RECALLS.map((r) => (
                <li key={r.recallNumber} className="rounded-lg border border-sovereign-800 px-3 py-2">
                  <p className="font-medium text-white">{r.recallNumber}</p>
                  <p className="text-xs text-slate-400">{r.product}</p>
                  <p className="mt-1 text-[10px] uppercase text-amber-300">{r.severity}</p>
                </li>
              ))}
            </ul>
          </GlassPanel>
        </div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {highlights.map((h) => (
            <GlassPanel key={h.title} title={h.title} accent={h.accent}>
              <p className="text-sm leading-relaxed text-slate-400">{h.body}</p>
            </GlassPanel>
          ))}
        </div>
      </div>
    </EnterprisePortalShell>
  );
}

function Metric({
  label,
  value,
  suffix,
  pulse,
}: {
  label: string;
  value: number;
  suffix: string;
  pulse?: boolean;
}) {
  return (
    <div className="glass-panel rounded-xl border border-sovereign-800/80 p-4">
      <p className="text-[10px] uppercase tracking-wider text-slate-500">{label}</p>
      <p className="mt-2 flex items-baseline gap-1 text-2xl font-semibold text-white">
        {value.toLocaleString()}
        {suffix}
        {pulse && <span className="ml-2 inline-block h-2 w-2 animate-ping rounded-full bg-emerald-400" />}
      </p>
    </div>
  );
}
