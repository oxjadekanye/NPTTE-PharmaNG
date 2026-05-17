"use client";

import { useEffect, useState } from "react";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { approveOnboarding, fetchPendingApprovals } from "@/services/command-center";

type Row = { id: string; organisation_name?: string; status?: string };

export default function ApprovalsPage() {
  const [rows, setRows] = useState<Row[]>([]);

  const load = () => fetchPendingApprovals().then((r) => setRows((r.data as Row[]) ?? []));
  useEffect(() => {
    load();
  }, []);

  return (
    <RegulatorGuard permission="regulatory.write">
      <CommandShell title="Approval Workflows">
        <div className="space-y-3">
          {rows.map((row) => (
            <div
              key={row.id}
              className="flex items-center justify-between rounded-lg border border-sovereign-800 bg-sovereign-900/50 px-4 py-3"
            >
              <div>
                <p className="font-medium">{row.organisation_name ?? row.id}</p>
                <p className="text-xs text-slate-500">{row.status}</p>
              </div>
              <button
                type="button"
                onClick={() => approveOnboarding(row.id).then(load)}
                className="rounded bg-sovereign-accent px-3 py-1.5 text-xs font-medium text-sovereign-950"
              >
                Approve
              </button>
            </div>
          ))}
        </div>
      </CommandShell>
    </RegulatorGuard>
  );
}
