"use client";

import dynamic from "next/dynamic";
import { useMemo, useState } from "react";
import { HOTSPOTS, LOGISTICS_ROUTES, STATE_RISKS } from "@/demo/nigeria-intelligence";
import type { Hotspot } from "./ThreatMap";
import { StateRiskPanel } from "./StateRiskPanel";
import type { MapPoint, MapRoute } from "./ThreatMapInner";
import type { DemoStateRisk } from "@/demo/types";

const MapInner = dynamic(() => import("./ThreatMapInner"), {
  ssr: false,
  loading: () => (
    <div className="flex h-[520px] items-center justify-center rounded-xl border border-sovereign-800 bg-sovereign-900 text-slate-500">
      Loading national threat map…
    </div>
  ),
});

function riskColor(score: number) {
  if (score >= 70) return "#ef4444";
  if (score >= 50) return "#f59e0b";
  return "#22c55e";
}

export function NigeriaThreatMap({ apiHotspots = [] }: { apiHotspots?: Hotspot[] }) {
  const [selected, setSelected] = useState<DemoStateRisk | undefined>(STATE_RISKS[0]);

  const points = useMemo(() => {
    const apiPoints: MapPoint[] = apiHotspots
      .map((h) => ({
        lat: Number(h.latitude),
        lng: Number(h.longitude),
        count: h.count ?? 1,
        label: `API hotspot · ${h.count ?? 1} signals`,
        color: "#ef4444",
      }))
      .filter((p) => !Number.isNaN(p.lat) && !Number.isNaN(p.lng));

    const demoHotspots: MapPoint[] = HOTSPOTS.map((h) => ({
      lat: h.lat,
      lng: h.lng,
      count: h.intensity,
      label: h.label,
      color: h.type === "seizure" ? "#8b5cf6" : h.type === "online_pharmacy" ? "#f97316" : "#ef4444",
      pulse: h.intensity > 70,
    }));

    const statePoints: MapPoint[] = STATE_RISKS.map((s) => ({
      lat: s.lat,
      lng: s.lng,
      count: s.riskScore,
      label: `${s.state} · risk ${s.riskScore} · ${s.pharmacyCount} pharmacies`,
      color: riskColor(s.riskScore),
      pulse: s.riskScore >= 70,
    }));

    return [...apiPoints, ...demoHotspots, ...statePoints];
  }, [apiHotspots]);

  const routes: MapRoute[] = LOGISTICS_ROUTES.map((r) => ({
    from: r.from,
    to: r.to,
    label: r.label,
  }));

  return (
    <div className="grid gap-4 lg:grid-cols-4">
      <div className="lg:col-span-3">
        <div className="h-[520px] overflow-hidden rounded-xl border border-sovereign-800 shadow-xl">
          <MapInner points={points} routes={routes} />
        </div>
        {selected && (
          <p className="mt-2 text-sm text-slate-400">
            <span className="font-semibold text-white">{selected.state}</span> — counterfeit signals{" "}
            {selected.counterfeitCount}, shortages {selected.shortageCount} (DEMO)
          </p>
        )}
      </div>
      <StateRiskPanel states={STATE_RISKS} selected={selected?.state} onSelect={setSelected} />
    </div>
  );
}
