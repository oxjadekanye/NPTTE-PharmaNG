"use client";

import dynamic from "next/dynamic";
import { useCallback, useEffect, useMemo, useState } from "react";
import { fetchMapMarkers, type MapMarker } from "@/services/command-orchestration";
import { useExplorerDrawerStore } from "@/store/explorer-drawer-store";
import type { MapPoint } from "./ThreatMapInner";

const MapInner = dynamic(() => import("./ThreatMapInner"), {
  ssr: false,
  loading: () => (
    <div className="flex h-[480px] items-center justify-center rounded-xl border border-sovereign-800 bg-sovereign-900 text-slate-500">
      Loading operational map…
    </div>
  ),
});

const LAYER_LABELS: Record<string, string> = {
  operational: "National operational",
  counterfeit: "Counterfeit hotspots",
  recalls: "Recall impact",
  shortage: "Shortage pressure",
  investigations: "Investigations",
  enforcement: "Enforcement deployment",
  customs: "Customs / border",
};

function severityColor(sev: string) {
  if (sev === "critical") return "#ef4444";
  if (sev === "high") return "#f97316";
  if (sev === "medium") return "#eab308";
  return "#22c55e";
}

export function OperationalMap({
  layer = "operational",
  heightClass = "h-[520px]",
}: {
  layer?: string;
  heightClass?: string;
}) {
  const [markers, setMarkers] = useState<MapMarker[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<MapMarker | null>(null);
  const openDrawer = useExplorerDrawerStore((s) => s.openDrawer);

  const load = useCallback(async () => {
    setLoading(true);
    const res = await fetchMapMarkers(layer, true);
    if (res.success && res.data) {
      setMarkers(res.data.markers ?? []);
    }
    setLoading(false);
  }, [layer]);

  useEffect(() => {
    void load();
  }, [load]);

  const points: MapPoint[] = useMemo(
    () =>
      markers.map((m) => ({
        lat: m.lat,
        lng: m.lng,
        count: m.cluster ? m.count ?? 3 : Math.max(1, m.risk_score / 10),
        label: m.cluster
          ? `${m.organisation} (${m.count})`
          : `${m.title || m.organisation} · ${m.severity}`,
        color: severityColor(m.severity),
        pulse: m.severity === "critical",
      })),
    [markers]
  );

  const openExplorer = () => {
    if (!selected?.explorer_entity_type || !selected.explorer_entity_id) return;
    openDrawer({
      entityType: selected.explorer_entity_type,
      entityId: selected.explorer_entity_id,
      title: selected.title || selected.organisation,
    });
  };

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-xs text-slate-500">{LAYER_LABELS[layer] ?? layer} · clustered markers</p>
        <button
          type="button"
          onClick={() => void load()}
          className="text-xs text-sovereign-accent hover:underline"
        >
          Refresh map
        </button>
      </div>
      <div className={`relative overflow-hidden rounded-xl border border-sovereign-800 ${heightClass}`}>
        {!loading && <MapInner points={points} />}
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-sovereign-950/80 text-slate-500">
            Hydrating markers…
          </div>
        )}
      </div>
      {markers.length > 0 && (
        <ul className="max-h-32 space-y-1 overflow-y-auto text-[11px] text-slate-400">
          {markers.slice(0, 12).map((m) => (
            <li key={m.id}>
              <button
                type="button"
                className="w-full rounded px-1 text-left hover:bg-sovereign-800/50 hover:text-slate-200"
                onClick={() => setSelected(m)}
              >
                {m.title || m.organisation} · {m.status} · risk {m.risk_score}
              </button>
            </li>
          ))}
        </ul>
      )}
      {selected && (
        <div className="rounded-lg border border-sovereign-700 bg-sovereign-900/60 p-3 text-xs text-slate-300">
          <p className="font-medium text-white">{selected.title || selected.organisation}</p>
          <p className="mt-1 text-slate-500">
            {selected.severity} · {selected.status}
            {selected.assigned_officer ? ` · ${selected.assigned_officer}` : ""}
          </p>
          <div className="mt-2 flex gap-3">
            {selected.explorer_entity_id && (
              <button type="button" className="text-sovereign-accent hover:underline" onClick={openExplorer}>
                Open in explorer →
              </button>
            )}
            <button type="button" className="text-slate-500 hover:text-slate-300" onClick={() => setSelected(null)}>
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
