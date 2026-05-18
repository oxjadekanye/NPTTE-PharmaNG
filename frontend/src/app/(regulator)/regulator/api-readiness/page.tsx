"use client";

import { useEffect, useState } from "react";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { fetchApiReadiness } from "@/services/pilot-readiness";

export default function ApiReadinessPage() {
  const [data, setData] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    fetchApiReadiness().then((r) => r.success && setData(r.data)).catch(() => setData(null));
  }, []);

  return (
    <RegulatorGuard>
      <CommandShell title="API Readiness Review">
        <div className="overflow-hidden rounded-xl border border-sovereign-800">
          <table className="w-full text-left text-sm">
            <thead className="bg-sovereign-900 text-xs uppercase text-slate-500">
              <tr>
                <th className="px-3 py-2">Group</th>
                <th className="px-3 py-2">Auth</th>
                <th className="px-3 py-2">Health</th>
              </tr>
            </thead>
            <tbody>
              {((data?.groups as Record<string, string>[]) ?? []).map((g) => (
                <tr key={g.group} className="border-t border-sovereign-800">
                  <td className="px-3 py-2 font-mono text-xs">{g.prefix}</td>
                  <td className="px-3 py-2">{g.auth}</td>
                  <td className="px-3 py-2">{g.endpoint_health}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CommandShell>
    </RegulatorGuard>
  );
}
