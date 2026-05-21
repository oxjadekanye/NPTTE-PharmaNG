"use client";

import { useEffect, useState } from "react";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { OperationalSkeleton } from "@/components/ui/OperationalSkeleton";
import { useRealtimeFeed } from "@/hooks/useRealtimeFeed";
import { fetchAlertCenter } from "@/services/national-operations";

export default function AlertCenterPage() {
  const [data, setData] = useState<{
    alerts: unknown[];
    unread_count: number;
    grouped: Record<string, unknown[]>;
  } | null>(null);
  const [filter, setFilter] = useState("");
  const { feed } = useRealtimeFeed({ channels: "recall_alert,national_alert" });

  useEffect(() => {
    fetchAlertCenter(filter ? { alert_type: filter } : undefined).then((r) => {
      if (r.success && r.data) setData(r.data);
    });
  }, [filter, feed?.polled_at]);

  return (
    <RegulatorGuard>
      <CommandShell
        title="National alert center"
        subtitle="Realtime polling · grouped operational alerts"
      >
        <div className="mb-4 flex gap-2">
          {["", "recall", "enforcement", "shortage"].map((f) => (
            <button
              key={f || "all"}
              type="button"
              onClick={() => setFilter(f)}
              className={`rounded-lg px-3 py-1 text-xs ${
                filter === f
                  ? "bg-sky-600 text-white"
                  : "border border-sovereign-700 text-slate-400"
              }`}
            >
              {f || "All"}
            </button>
          ))}
        </div>
        {!data ? (
          <OperationalSkeleton />
        ) : (
          <>
            <p className="mb-4 text-sm text-slate-400">{data.unread_count} alerts in view</p>
            <ul className="space-y-2">
              {(data.alerts as { id: string; title: string; severity: string; priority: string }[]).map(
                (a) => (
                  <li
                    key={a.id}
                    className="rounded-xl border border-sovereign-800 bg-sovereign-900/50 px-4 py-3 transition hover:border-rose-500/30"
                  >
                    <p className="font-medium text-white">{a.title}</p>
                    <p className="text-xs text-slate-500">
                      {a.severity} · priority {a.priority}
                    </p>
                  </li>
                )
              )}
            </ul>
          </>
        )}
      </CommandShell>
    </RegulatorGuard>
  );
}
