"use client";

import { memo, useEffect, useState } from "react";
import { OperationalSkeleton } from "@/components/ui/OperationalSkeleton";
import { apiRequest } from "@/services/api-client";

function EvidenceTimelineInner() {
  const [rows, setRows] = useState<unknown[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiRequest<{ timeline: unknown[] }>("/mobile/evidence/timeline/")
      .then((r) => setRows(r.data?.timeline ?? []))
      .catch(() => setRows([]))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <OperationalSkeleton rows={4} />;
  if (rows.length === 0) return <p className="text-sm text-slate-500">No field evidence on record.</p>;

  return (
    <ul className="space-y-2">
      {(rows as {
        id: string;
        category_label: string;
        serial_number: string;
        captured_at: string;
        sync_status: string;
      }[]).map((e) => (
        <li key={e.id} className="rounded-lg border border-sovereign-800 px-3 py-2 text-xs">
          <p className="font-medium text-slate-200">{e.category_label}</p>
          <p className="text-slate-500">
            {e.serial_number || "—"} · {e.sync_status} · {new Date(e.captured_at).toLocaleString()}
          </p>
        </li>
      ))}
    </ul>
  );
}

export const EvidenceTimeline = memo(EvidenceTimelineInner);
