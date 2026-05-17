"use client";

import dynamic from "next/dynamic";
import { useMemo } from "react";

export type Hotspot = {
  latitude: number | string;
  longitude: number | string;
  count?: number;
  outcome?: string;
};

const MapInner = dynamic(() => import("./ThreatMapInner"), { ssr: false, loading: () => (
  <div className="flex h-[480px] items-center justify-center rounded-xl border border-sovereign-800 bg-sovereign-900 text-slate-500">
    Loading threat map…
  </div>
)});

export function ThreatMap({ hotspots }: { hotspots: Hotspot[] }) {
  const points = useMemo(
    () =>
      hotspots
        .map((h) => ({
          lat: Number(h.latitude),
          lng: Number(h.longitude),
          count: h.count ?? 1,
        }))
        .filter((p) => !Number.isNaN(p.lat) && !Number.isNaN(p.lng)),
    [hotspots]
  );

  return (
    <div className="h-[480px] overflow-hidden rounded-xl border border-sovereign-800">
      <MapInner points={points} />
    </div>
  );
}
