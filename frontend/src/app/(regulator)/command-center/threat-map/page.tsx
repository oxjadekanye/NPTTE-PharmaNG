"use client";

import { useEffect, useState } from "react";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { ThreatMap, type Hotspot } from "@/components/maps/ThreatMap";
import { fetchThreatMap } from "@/services/command-center";

export default function ThreatMapPage() {
  const [hotspots, setHotspots] = useState<Hotspot[]>([]);

  useEffect(() => {
    fetchThreatMap().then((res) => {
      const data = res.data as { counterfeit_hotspots?: Hotspot[] };
      setHotspots(data.counterfeit_hotspots ?? []);
    });
  }, []);

  return (
    <RegulatorGuard>
      <CommandShell title="Realtime Threat Map">
        <p className="mb-4 text-sm text-slate-400">
          Counterfeit verification clusters · diversion signals · regional risk overlays
        </p>
        <ThreatMap hotspots={hotspots} />
      </CommandShell>
    </RegulatorGuard>
  );
}
