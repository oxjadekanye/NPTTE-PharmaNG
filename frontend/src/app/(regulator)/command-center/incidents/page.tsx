"use client";

import { useEffect, useState } from "react";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { fetchActiveIncidents } from "@/services/command-center";
import type { IncidentRow } from "@/shared/types";

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<IncidentRow[]>([]);

  useEffect(() => {
    fetchActiveIncidents().then((res) => setIncidents((res.data.incidents as IncidentRow[]) ?? []));
  }, []);

  return (
    <RegulatorGuard>
      <CommandShell title="Active Incidents">
        <div className="overflow-hidden rounded-xl border border-sovereign-800">
          <table className="w-full text-left text-sm">
            <thead className="bg-sovereign-900 text-xs uppercase text-slate-500">
              <tr>
                <th className="px-4 py-3">Code</th>
                <th className="px-4 py-3">Title</th>
                <th className="px-4 py-3">Severity</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Threat</th>
              </tr>
            </thead>
            <tbody>
              {incidents.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-slate-500">
                    No active incidents
                  </td>
                </tr>
              ) : (
                incidents.map((i) => (
                  <tr key={i.id} className="border-t border-sovereign-800 hover:bg-sovereign-900/50">
                    <td className="px-4 py-3 font-mono text-xs">{i.code}</td>
                    <td className="px-4 py-3">{i.title}</td>
                    <td className="px-4 py-3 capitalize">{i.severity}</td>
                    <td className="px-4 py-3">{i.status}</td>
                    <td className="px-4 py-3">{i.threat_score}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </CommandShell>
    </RegulatorGuard>
  );
}
