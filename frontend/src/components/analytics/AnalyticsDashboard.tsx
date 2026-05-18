"use client";

import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  CHART_FRAUD_TREND,
  CHART_SHORTAGE_FORECAST,
  CHART_SUPPLY_FLOW,
  CHART_VERIFICATION_TREND,
  NATIONAL_KPIS,
} from "@/demo/nigeria-intelligence";

const chartWrap = "rounded-xl border border-sovereign-800 bg-sovereign-900/60 p-5 shadow-lg";

export function AnalyticsDashboard() {
  return (
    <div className="space-y-6">
      <p className="text-xs text-slate-500">
        Charts blend API analytics where available with simulated national datasets (DEMO).
      </p>
      <div className="grid gap-6 lg:grid-cols-2">
        <div className={chartWrap}>
          <h3 className="mb-3 text-sm font-semibold text-white">Verification scan trends</h3>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={CHART_VERIFICATION_TREND}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="day" stroke="#94a3b8" fontSize={11} />
                <YAxis stroke="#94a3b8" fontSize={11} tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
                <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
                <Area type="monotone" dataKey="scans" stroke="#38bdf8" fill="#0ea5e933" />
                <Area type="monotone" dataKey="flagged" stroke="#ef4444" fill="#ef444433" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className={chartWrap}>
          <h3 className="mb-3 text-sm font-semibold text-white">Fraud trend analysis</h3>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={CHART_FRAUD_TREND}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="month" stroke="#94a3b8" fontSize={11} />
                <YAxis stroke="#94a3b8" fontSize={11} />
                <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
                <Line type="monotone" dataKey="cases" stroke="#f59e0b" strokeWidth={2} dot />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className={chartWrap}>
          <h3 className="mb-3 text-sm font-semibold text-white">Shortage forecasting by state</h3>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={CHART_SHORTAGE_FORECAST}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="state" stroke="#94a3b8" fontSize={11} />
                <YAxis stroke="#94a3b8" fontSize={11} />
                <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
                <Legend />
                <Bar dataKey="current" fill="#38bdf8" name="Current" radius={[4, 4, 0, 0]} />
                <Bar dataKey="forecast" fill="#f97316" name="Forecast" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className={chartWrap}>
          <h3 className="mb-3 text-sm font-semibold text-white">Supply chain movement</h3>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={CHART_SUPPLY_FLOW} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis type="number" stroke="#94a3b8" fontSize={11} />
                <YAxis type="category" dataKey="stage" stroke="#94a3b8" fontSize={11} width={90} />
                <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
                <Bar dataKey="volume" fill="#10b981" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-lg border border-sovereign-800 bg-sovereign-900/50 p-4 text-center">
          <p className="text-xs text-slate-500">Customs interceptions (30d)</p>
          <p className="mt-1 font-mono text-2xl text-white">{NATIONAL_KPIS.customsInterceptions}</p>
        </div>
        <div className="rounded-lg border border-sovereign-800 bg-sovereign-900/50 p-4 text-center">
          <p className="text-xs text-slate-500">High-risk states monitored</p>
          <p className="mt-1 font-mono text-2xl text-amber-400">8</p>
        </div>
        <div className="rounded-lg border border-sovereign-800 bg-sovereign-900/50 p-4 text-center">
          <p className="text-xs text-slate-500">Warehouse inspections (active)</p>
          <p className="mt-1 font-mono text-2xl text-white">{NATIONAL_KPIS.warehouseInspections}</p>
        </div>
      </div>
    </div>
  );
}
