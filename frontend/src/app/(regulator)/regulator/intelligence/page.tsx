"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import clsx from "clsx";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { GlassPanel } from "@/components/enterprise/GlassPanel";
import {
  fetchCounterfeitClusters,
  fetchIntelligenceSignals,
  fetchNationalRisk,
  fetchProductRisk,
  fetchRegionalRisk,
  runCorrelation,
} from "@/services/sovereign-intelligence";
import { useExplorerDrawerStore } from "@/store/explorer-drawer-store";

type RiskRow = {
  score?: number;
  status?: string;
  confidence?: number;
  reasons?: string[];
  region_state?: string;
};

function statusColor(status?: string) {
  if (status === "critical" || status === "red") return "text-rose-300 bg-rose-500/20";
  if (status === "amber") return "text-amber-300 bg-amber-500/20";
  return "text-emerald-300 bg-emerald-500/20";
}

export default function IntelligenceDashboardPage() {
  const openDrawer = useExplorerDrawerStore((s) => s.openDrawer);
  const [risk, setRisk] = useState<RiskRow | null>(null);
  const [regions, setRegions] = useState<RiskRow[]>([]);
  const [products, setProducts] = useState<Record<string, unknown>[]>([]);
  const [signals, setSignals] = useState<Record<string, unknown>[]>([]);
  const [clusters, setClusters] = useState<Record<string, unknown>[]>([]);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    fetchNationalRisk().then((r) => setRisk((r.data as RiskRow) ?? null));
    fetchRegionalRisk().then((r) => setRegions(((r.data as { regions?: RiskRow[] })?.regions ?? []) as RiskRow[]));
    fetchProductRisk().then((r) => setProducts((r.data?.products as Record<string, unknown>[]) ?? []));
    fetchIntelligenceSignals().then((r) => setSignals((r.data?.signals as Record<string, unknown>[]) ?? []));
    fetchCounterfeitClusters().then((r) => setClusters((r.data?.clusters as Record<string, unknown>[]) ?? []));
  }, []);

  return (
    <RegulatorGuard>
      <CommandShell title="Sovereign Intelligence">
        <div className="mb-4 flex flex-wrap gap-3 text-xs">
          <Link href="/regulator/intelligence/narratives" className="text-sovereign-accent hover:underline">
            Narratives →
          </Link>
          <Link href="/regulator/intelligence/clusters" className="text-sovereign-accent hover:underline">
            Clusters →
          </Link>
          <Link href="/regulator/enforcement" className="text-sovereign-accent hover:underline">
            Enforcement →
          </Link>
        </div>
        <div className="grid gap-4 lg:grid-cols-3">
          <GlassPanel title="National risk" subtitle="GET /intelligence/national-risk/" accent="rose" className="lg:col-span-2">
            <div
              role="button"
              tabIndex={0}
              className="cursor-pointer rounded-lg outline-none transition hover:bg-sovereign-800/30"
              onClick={() =>
                openDrawer({ entityType: "national_risk", entityId: "national-risk-current", title: "National risk" })
              }
              onKeyDown={(ev) => {
                if (ev.key === "Enter" || ev.key === " ") {
                  ev.preventDefault();
                  openDrawer({
                    entityType: "national_risk",
                    entityId: "national-risk-current",
                    title: "National risk",
                  });
                }
              }}
            >
              <div className="flex flex-wrap items-center gap-4">
                <p className="text-4xl font-semibold tabular-nums text-white">{risk?.score ?? "—"}</p>
                <span className={clsx("rounded-full px-3 py-1 text-xs uppercase", statusColor(risk?.status))}>
                  {risk?.status ?? "—"}
                </span>
                <span className="text-xs text-slate-500">Confidence {risk?.confidence ?? "—"}%</span>
                <button
                  type="button"
                  disabled={busy}
                  onClick={(ev) => {
                    ev.stopPropagation();
                    setBusy(true);
                    runCorrelation().finally(() => {
                      setBusy(false);
                      window.location.reload();
                    });
                  }}
                  className="ml-auto rounded-lg border border-sovereign-700 px-3 py-1 text-xs text-sovereign-accent disabled:opacity-50"
                >
                  Run correlation
                </button>
              </div>
              <ul className="mt-4 space-y-1 text-xs text-slate-400">
                {(risk?.reasons ?? []).map((reason, i) => (
                  <li key={i}>• {reason}</li>
                ))}
              </ul>
            </div>
          </GlassPanel>
          <GlassPanel title="Live signals" subtitle="Streambus + DB">
            <ul className="max-h-48 space-y-2 overflow-y-auto text-xs">
              {signals.length === 0 && <li className="text-slate-500">No active signals</li>}
              {signals.map((s) => (
                <li key={String(s.id)}>
                  <button
                    type="button"
                    className="w-full rounded border border-sovereign-700/50 px-2 py-1 text-left outline-none transition hover:border-sovereign-accent/50 hover:bg-sovereign-800/40"
                    onClick={() =>
                      openDrawer({
                        entityType: "intelligence_signal",
                        entityId: String(s.id),
                        title: String(s.title),
                      })
                    }
                  >
                    <p className="font-medium text-slate-200">{String(s.title)}</p>
                    <p className="text-slate-500">
                      {String(s.severity)} · {String(s.signal_type)}
                    </p>
                  </button>
                </li>
              ))}
            </ul>
          </GlassPanel>
          <GlassPanel title="Regional heat" className="lg:col-span-2">
            <div className="grid gap-2 sm:grid-cols-2">
              {regions.map((region) => (
                <button
                  key={region.region_state ?? region.score}
                  type="button"
                  className="rounded-lg border border-sovereign-700/50 px-3 py-2 text-left text-xs outline-none transition hover:border-sovereign-accent/50 hover:bg-sovereign-800/40"
                  onClick={() =>
                    openDrawer({
                      entityType: "regional_risk",
                      entityId: String(region.region_state ?? ""),
                      title: `Regional · ${region.region_state}`,
                    })
                  }
                >
                  <p className="font-medium text-white">{region.region_state}</p>
                  <p className="text-slate-400">
                    Score {region.score} · <span className={statusColor(region.status)}>{region.status}</span>
                  </p>
                </button>
              ))}
            </div>
          </GlassPanel>
          <GlassPanel title="Counterfeit clusters" accent="amber">
            {clusters.slice(0, 4).map((c) => (
              <p key={String(c.cluster_code)} className="text-xs text-slate-400">
                {String(c.cluster_code)} — {String(c.suspicious_count)} suspicious
              </p>
            ))}
            {clusters.length === 0 && <p className="text-xs text-slate-500">No open clusters</p>}
          </GlassPanel>
          <GlassPanel title="Product risk" className="lg:col-span-3">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="text-slate-500">
                  <tr>
                    <th className="py-1">Product</th>
                    <th>Score</th>
                    <th>Status</th>
                    <th>Counterfeit %</th>
                  </tr>
                </thead>
                <tbody>
                  {products.map((p) => (
                    <tr
                      key={String(p.product_id)}
                      className="cursor-pointer border-t border-sovereign-800 hover:bg-sovereign-800/40"
                      role="button"
                      tabIndex={0}
                      onClick={() =>
                        openDrawer({
                          entityType: "product",
                          entityId: String(p.product_id),
                          title: String(p.name),
                        })
                      }
                      onKeyDown={(ev) => {
                        if (ev.key === "Enter" || ev.key === " ") {
                          ev.preventDefault();
                          openDrawer({
                            entityType: "product",
                            entityId: String(p.product_id),
                            title: String(p.name),
                          });
                        }
                      }}
                    >
                      <td className="py-2 text-slate-200">{String(p.name)}</td>
                      <td>{String(p.score)}</td>
                      <td>{String(p.status)}</td>
                      <td>{String(p.counterfeit_probability)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </GlassPanel>
        </div>
      </CommandShell>
    </RegulatorGuard>
  );
}
