"use client";

import { useEffect, useState } from "react";
import { GlassPanel } from "@/components/enterprise/GlassPanel";
import { OperationalKeyValuePanel, OperationalListPanel } from "@/components/shared/OperationalDisplay";
import {
  fetchApiReadiness,
  fetchPerformanceReadiness,
  fetchPilotReadiness,
  fetchSecurityReadiness,
} from "@/services/pilot-readiness";

export function PilotReadinessDashboard() {
  const [report, setReport] = useState<Record<string, unknown> | null>(null);
  const [security, setSecurity] = useState<Record<string, unknown> | null>(null);
  const [performance, setPerformance] = useState<Record<string, unknown> | null>(null);
  const [api, setApi] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    fetchPilotReadiness().then((r) => r.success && setReport(r.data)).catch(() => setReport(null));
    fetchSecurityReadiness().then((r) => r.success && setSecurity(r.data)).catch(() => setSecurity(null));
    fetchPerformanceReadiness().then((r) => r.success && setPerformance(r.data)).catch(() => setPerformance(null));
    fetchApiReadiness().then((r) => r.success && setApi(r.data)).catch(() => setApi(null));
  }, []);

  const score = Number(report?.operational_readiness_score ?? 0);

  return (
    <div className="space-y-6">
      <div className="glass-panel operational-glow rounded-2xl border border-sovereign-accent/30 p-6">
        <p className="text-[10px] uppercase tracking-widest text-sovereign-accent">Pilot readiness score</p>
        <p className="mt-2 text-5xl font-semibold tabular-nums text-white">{score || "—"}</p>
        <p className="mt-2 text-sm text-slate-400">
          Backend: {String(report?.backend_health ?? "—")} · DB:{" "}
          {String((report?.database_health as { status?: string })?.status ?? "—")}
        </p>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <GlassPanel title="Active modules" subtitle="Production modules enabled">
          <ul className="space-y-1 text-sm text-slate-300">
            {((report?.active_modules as { label: string }[]) ?? []).map((m) => (
              <li key={m.label}>✓ {m.label}</li>
            ))}
          </ul>
        </GlassPanel>
        <GlassPanel title="Pending risks" accent="amber">
          <ul className="space-y-1 text-sm text-amber-100/90">
            {((report?.pending_risks as { item: string }[]) ?? []).map((r) => (
              <li key={r.item}>• {r.item}</li>
            ))}
            {!(report?.pending_risks as unknown[])?.length && <li>None flagged</li>}
          </ul>
        </GlassPanel>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {(["regulator", "pharmacy", "manufacturer", "citizen"] as const).map((key) => (
          <GlassPanel key={key} title={`${key} demo checklist`}>
            <ol className="list-decimal space-y-1 pl-4 text-xs text-slate-400">
              {(((report?.demo_checklists as Record<string, string[]>) ?? {})[key] ?? []).map((step) => (
                <li key={step}>{step}</li>
              ))}
            </ol>
          </GlassPanel>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <GlassPanel title="Security (no secrets)" subtitle="Posture display only">
          <OperationalKeyValuePanel data={security} emptyMessage="Security posture loading…" />
        </GlassPanel>
        <GlassPanel title="Performance readiness">
          <OperationalKeyValuePanel data={performance} emptyMessage="Performance metrics loading…" />
        </GlassPanel>
        <GlassPanel title="API groups">
          <OperationalListPanel
            items={((api?.groups as unknown[]) ?? []).slice(0, 6) as Record<string, unknown>[]}
            emptyMessage="API readiness loading…"
            renderItem={(row) => (
              <p className="font-medium text-slate-300">{String(row.name ?? row.group ?? row.path ?? "Group")}</p>
            )}
          />
        </GlassPanel>
      </div>
    </div>
  );
}
