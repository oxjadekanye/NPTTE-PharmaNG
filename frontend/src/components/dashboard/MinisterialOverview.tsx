"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { AnimatedMetricCard } from "@/components/ui/AnimatedMetricCard";
import {
  CHART_SHORTAGE_FORECAST,
  NATIONAL_KPIS,
  computeNationalStatus,
} from "@/demo/nigeria-intelligence";
import { openExplorerFromContext } from "@/services/explorer-routing";
import { useExplorerDrawerStore } from "@/store/explorer-drawer-store";
import { NationalStatusBanner } from "./NationalStatusBanner";

const URGENT_ACTIONS = [
  "Approve emergency insulin redistribution — Enugu (FMOH)",
  "Ministerial briefing on Lagos counterfeit antimalarial cluster",
  "Coordinate NAFDAC–Customs joint inspection — Apapa port",
  "Publish public verification advisory — Kano online pharmacy case",
  "Review national cold-chain compliance — Q2 2026",
];

export function MinisterialOverview() {
  const kpis = NATIONAL_KPIS;
  const status = computeNationalStatus(kpis);
  const openDrawer = useExplorerDrawerStore((s) => s.openDrawer);

  return (
    <div className="space-y-6">
      <NationalStatusBanner status={status} />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <AnimatedMetricCard
          label="National verifications (24h)"
          numericValue={kpis.verificationsToday}
          pulse
          explorerContext="verifications_24h"
        />
        <AnimatedMetricCard
          label="Compliance rate"
          numericValue={kpis.complianceRate}
          decimals={1}
          suffix="%"
          explorerContext="national_status"
        />
        <AnimatedMetricCard
          label="Scan success rate"
          numericValue={kpis.scanSuccessRate}
          decimals={1}
          suffix="%"
          explorerContext="verifications_24h"
        />
        <AnimatedMetricCard
          label="Counterfeit reduction (YoY)"
          numericValue={kpis.counterfeitReductionPct}
          decimals={1}
          suffix="%"
          severity="normal"
          explorerContext="counterfeit_detections"
        />
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-sovereign-800 bg-sovereign-900/60 p-5">
          <h3 className="text-sm font-semibold text-white">Public health risk indicators</h3>
          <ul className="mt-4 space-y-2 text-sm text-slate-300">
            <li>
              <button
                type="button"
                className="w-full rounded px-1 text-left hover:bg-sovereign-800/50 hover:text-sovereign-accent"
                onClick={() => void openExplorerFromContext(openDrawer, "recalls", "Active recalls")}
              >
                Active recalls: {kpis.recallsActive} (DEMO)
              </button>
            </li>
            <li>
              <button
                type="button"
                className="w-full rounded px-1 text-left hover:bg-sovereign-800/50 hover:text-sovereign-accent"
                onClick={() => void openExplorerFromContext(openDrawer, "open_alerts", "Shortage alerts")}
              >
                Regional shortage alerts: {kpis.shortageAlerts}
              </button>
            </li>
            <li>
              <button
                type="button"
                className="w-full rounded px-1 text-left hover:bg-sovereign-800/50 hover:text-sovereign-accent"
                onClick={() => void openExplorerFromContext(openDrawer, "active_investigations", "Investigations")}
              >
                Active investigations: {kpis.activeInvestigations}
              </button>
            </li>
            <li>
              <button
                type="button"
                className="w-full rounded px-1 text-left hover:bg-sovereign-800/50 hover:text-sovereign-accent"
                onClick={() =>
                  void openExplorerFromContext(openDrawer, "counterfeit_detections", "Counterfeit detections")
                }
              >
                Counterfeit detections (30d): {kpis.counterfeitDetections}
              </button>
            </li>
          </ul>
        </div>
        <div className="rounded-xl border border-sovereign-800 bg-sovereign-900/60 p-5">
          <h3 className="text-sm font-semibold text-white">Top 5 urgent actions</h3>
          <ol className="mt-4 list-decimal space-y-2 pl-5 text-sm text-slate-300">
            {URGENT_ACTIONS.map((a) => (
              <li key={a}>
                <button
                  type="button"
                  className="text-left hover:text-sovereign-accent"
                  onClick={() => void openExplorerFromContext(openDrawer, "enforcement_recommendation", a)}
                >
                  {a}
                </button>
              </li>
            ))}
          </ol>
        </div>
      </div>
      <div className="rounded-xl border border-sovereign-800 bg-sovereign-900/60 p-5">
        <h3 className="mb-4 text-sm font-semibold text-white">Regional shortage forecast (DEMO)</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={CHART_SHORTAGE_FORECAST}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="state" stroke="#94a3b8" fontSize={11} />
              <YAxis stroke="#94a3b8" fontSize={11} />
              <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
              <Bar dataKey="current" fill="#38bdf8" name="Current stock index" radius={[4, 4, 0, 0]} />
              <Bar dataKey="forecast" fill="#f59e0b" name="7-day forecast" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
