"use client";

import { useEffect, useState } from "react";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { IncidentCenter } from "@/components/incidents/IncidentCenter";
import { fetchActiveIncidents } from "@/services/command-center";
import { useSimulatedRealtime } from "@/hooks/useSimulatedRealtime";
import type { IncidentRow } from "@/shared/types";

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<IncidentRow[]>([]);
  useSimulatedRealtime(true);

  useEffect(() => {
    fetchActiveIncidents()
      .then((res) => setIncidents((res.data.incidents as IncidentRow[]) ?? []))
      .catch(() => setIncidents([]));
  }, []);

  return (
    <RegulatorGuard>
      <CommandShell title="Incident Management Center">
        <p className="mb-4 text-sm text-slate-400">
          Enterprise incident workflow — severity, escalation, linked entities, audit timeline (DEMO blended with API).
        </p>
        <IncidentCenter apiIncidents={incidents} />
      </CommandShell>
    </RegulatorGuard>
  );
}
