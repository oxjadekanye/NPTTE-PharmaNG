"use client";

import { useEffect, useState } from "react";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { fetchApprovalQueue } from "@/services/tenancy";
import { apiRequest } from "@/services/api-client";

type QueueItem = {
  id: string;
  organisation_id: string;
  legal_name: string;
  organisation_type: string;
  status: string;
};

export default function TenantApprovalsPage() {
  const [queue, setQueue] = useState<QueueItem[]>([]);

  useEffect(() => {
    fetchApprovalQueue().then((r) => setQueue((r.data.queue as QueueItem[]) ?? []));
  }, []);

  async function approve(id: string) {
    await apiRequest(`/tenancy/regulator/approve/${id}/`, { method: "POST", body: "{}" });
    const r = await fetchApprovalQueue();
    setQueue((r.data.queue as QueueItem[]) ?? []);
  }

  return (
    <RegulatorGuard>
      <CommandShell title="Organisation approvals">
        <ul className="space-y-3">
          {queue.map((item) => (
            <li
              key={item.id}
              className="flex items-center justify-between rounded-xl border border-sovereign-800 bg-sovereign-900/60 px-4 py-3"
            >
              <div>
                <p className="font-medium">{item.legal_name}</p>
                <p className="text-xs text-slate-500">
                  {item.organisation_type} · {item.status}
                </p>
              </div>
              <button
                type="button"
                onClick={() => approve(item.id)}
                className="rounded-lg bg-sovereign-accent px-3 py-1.5 text-xs font-semibold text-sovereign-950"
              >
                Approve
              </button>
            </li>
          ))}
          {!queue.length && <li className="text-sm text-slate-500">No pending applications</li>}
        </ul>
      </CommandShell>
    </RegulatorGuard>
  );
}
