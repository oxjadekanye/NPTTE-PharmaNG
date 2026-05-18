"use client";

import { useEffect, useState } from "react";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { NigeriaThreatMap } from "@/components/maps/NigeriaThreatMap";
import { fetchThreatMap } from "@/services/command-center";
import type { Hotspot } from "@/components/maps/ThreatMap";
import { useSimulatedRealtime } from "@/hooks/useSimulatedRealtime";

export default function ThreatMapPage() {
  const [hotspots, setHotspots] = useState<Hotspot[]>([]);
  useSimulatedRealtime(true);

  useEffect(() => {
    fetchThreatMap()
      .then((res) => {
        const data = res.data as { counterfeit_hotspots?: Hotspot[] };
        setHotspots(data.counterfeit_hotspots ?? []);
      })
      .catch(() => setHotspots([]));
  }, []);

  return (
    <RegulatorGuard>
      <CommandShell title="National Threat Map">
        <p className="mb-4 text-sm text-slate-400">
          State risk, counterfeit heat, seizure locations, pharmacy density overlays &amp; logistics routes (DEMO + API).
        </p>
        <NigeriaThreatMap apiHotspots={hotspots} />
      </CommandShell>
    </RegulatorGuard>
  );
}
