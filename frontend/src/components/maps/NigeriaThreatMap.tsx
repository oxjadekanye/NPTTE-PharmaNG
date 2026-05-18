"use client";

import dynamic from "next/dynamic";
import { useMemo, useState } from "react";
import {
  CUSTOMS_MARKERS,
  HOTSPOTS,
  INVESTIGATION_ZONES,
  LOGISTICS_ROUTES,
  STATE_RISKS,
  WAREHOUSE_HUBS,
} from "@/demo/nigeria-intelligence";
import type { Hotspot } from "./ThreatMap";
import { StateRiskPanel } from "./StateRiskPanel";
import type { MapPoint, MapRoute } from "./ThreatMapInner";
import type { DemoStateRisk, MapIntelLayer } from "@/demo/types";

const MapInner = dynamic(() => import("./ThreatMapInner"), {
  ssr: false,
  loading: () => (
    <div className="flex h-[520px] items-center justify-center rounded-xl border border-sovereign-800 bg-sovereign-900 text-slate-500">
      Loading sovereign intelligence map…
    </div>
  ),
});

const LAYERS: { id: MapIntelLayer; label: string }[] = [
  { id: "risk", label: "State risk" },
  { id: "pharmacy_density", label: "Pharmacy density" },
  { id: "shortage", label: "Shortage heat" },
  { id: "customs", label: "Customs" },
  { id: "investigations", label: "Investigations" },
  { id: "logistics", label: "Logistics routes" },
];

function riskColor(score: number) {
  if (score >= 70) return "#ef4444";
  if (score >= 50) return "#f59e0b";
  return "#22c55e";
}

function toggleLayer(set: Set<MapIntelLayer>, id: MapIntelLayer) {
  const next = new Set(set);
  if (next.has(id)) next.delete(id);
  else next.add(id);
  if (next.size === 0) next.add("risk");
  return next;
}

export function NigeriaThreatMap({ apiHotspots = [] }: { apiHotspots?: Hotspot[] }) {
  const [selected, setSelected] = useState<DemoStateRisk | undefined>(STATE_RISKS[0]);
  const [layers, setLayers] = useState<Set<MapIntelLayer>>(
    () => new Set(["risk", "logistics", "customs", "investigations"])
  );

  const points = useMemo(() => {
    const out: MapPoint[] = [];

    if (layers.has("risk")) {
      const apiPoints: MapPoint[] = apiHotspots
        .map((h) => ({
          lat: Number(h.latitude),
          lng: Number(h.longitude),
          count: h.count ?? 1,
          label: `API hotspot · ${h.count ?? 1} signals`,
          color: "#ef4444",
        }))
        .filter((p) => !Number.isNaN(p.lat) && !Number.isNaN(p.lng));
      out.push(...apiPoints);

      const demoHotspots: MapPoint[] = HOTSPOTS.map((h) => ({
        lat: h.lat,
        lng: h.lng,
        count: h.intensity,
        label: h.label,
        color: h.type === "seizure" ? "#8b5cf6" : h.type === "online_pharmacy" ? "#f97316" : "#ef4444",
        pulse: h.intensity > 70,
      }));
      out.push(...demoHotspots);

      const statePoints: MapPoint[] = STATE_RISKS.map((s) => ({
        lat: s.lat,
        lng: s.lng,
        count: s.riskScore,
        label: `${s.state} · risk ${s.riskScore} · ${s.pharmacyCount} pharmacies`,
        color: riskColor(s.riskScore),
        pulse: s.riskScore >= 70,
      }));
      out.push(...statePoints);
    }

    if (layers.has("pharmacy_density")) {
      out.push(
        ...STATE_RISKS.map((s) => ({
          lat: s.lat + 0.04,
          lng: s.lng + 0.04,
          count: s.pharmacyCount / 40,
          label: `${s.state} · pharmacy density (sim)`,
          color: "#38bdf8",
          pulse: s.pharmacyCount > 350,
        }))
      );
    }

    if (layers.has("shortage")) {
      out.push(
        ...STATE_RISKS.filter((s) => s.shortageCount > 0).map((s) => ({
          lat: s.lat - 0.05,
          lng: s.lng - 0.05,
          count: 40 + s.shortageCount * 20,
          label: `${s.state} · shortage intensity`,
          color: "#facc15",
          pulse: true,
        }))
      );
    }

    if (layers.has("customs")) {
      out.push(
        ...CUSTOMS_MARKERS.map((h) => ({
          lat: h.lat,
          lng: h.lng,
          count: h.intensity,
          label: h.label,
          color: "#a78bfa",
          pulse: true,
        }))
      );
    }

    if (layers.has("investigations")) {
      out.push(
        ...INVESTIGATION_ZONES.map((h) => ({
          lat: h.lat,
          lng: h.lng,
          count: h.intensity,
          label: h.label,
          color: "#fb7185",
          pulse: true,
        }))
      );
    }

    if (layers.has("logistics")) {
      out.push(
        ...WAREHOUSE_HUBS.map((w) => ({
          lat: w.lat,
          lng: w.lng,
          count: w.throughput / 25,
          label: `${w.name} · hub`,
          color: "#34d399",
          pulse: w.throughput > 600,
        }))
      );
    }

    return out;
  }, [apiHotspots, layers]);

  const routes: MapRoute[] = useMemo(
    () =>
      layers.has("logistics")
        ? LOGISTICS_ROUTES.map((r) => ({
            from: r.from,
            to: r.to,
            label: r.label,
          }))
        : [],
    [layers]
  );

  return (
    <div className="grid gap-4 lg:grid-cols-4">
      <div className="lg:col-span-3">
        <div className="mb-3 flex flex-wrap gap-2">
          {LAYERS.map((L) => (
            <button
              key={L.id}
              type="button"
              onClick={() => setLayers((s) => toggleLayer(s, L.id))}
              className={`rounded-full border px-3 py-1 text-[10px] font-medium uppercase tracking-wide transition ${
                layers.has(L.id)
                  ? "border-sovereign-accent bg-sovereign-accent/15 text-sovereign-accent"
                  : "border-sovereign-700 text-slate-500 hover:border-sovereign-600"
              }`}
            >
              {L.label}
            </button>
          ))}
        </div>
        <div className="h-[520px] overflow-hidden rounded-xl border border-sovereign-800 shadow-xl">
          <MapInner points={points} routes={routes} />
        </div>
        {selected && (
          <p className="mt-2 text-sm text-slate-400">
            <span className="font-semibold text-white">{selected.state}</span> — counterfeit signals{" "}
            {selected.counterfeitCount}, shortages {selected.shortageCount}{" "}
            <span className="text-slate-600">(DEMO overlays)</span>
          </p>
        )}
      </div>
      <StateRiskPanel states={STATE_RISKS} selected={selected?.state} onSelect={setSelected} />
    </div>
  );
}
