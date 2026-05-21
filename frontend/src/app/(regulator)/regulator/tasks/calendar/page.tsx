"use client";

import { useEffect, useState } from "react";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { fetchTaskCalendar } from "@/services/operations";

export default function TaskCalendarPage() {
  const [entries, setEntries] = useState<unknown[]>([]);

  useEffect(() => {
    fetchTaskCalendar(30).then((r) => setEntries(r.data?.calendar ?? []));
  }, []);

  return (
    <RegulatorGuard>
      <CommandShell title="Operational calendar" subtitle="30-day field operations horizon">
        <ul className="space-y-2">
          {(entries as { id: string; title: string; due_at?: string; priority: string }[]).map(
            (e) => (
              <li
                key={e.id}
                className="flex justify-between rounded-lg border border-sovereign-800 px-4 py-2 text-sm"
              >
                <span className="text-slate-200">{e.title}</span>
                <span className="text-xs text-slate-500">
                  {e.due_at ? new Date(e.due_at).toLocaleDateString() : "—"} · {e.priority}
                </span>
              </li>
            )
          )}
        </ul>
      </CommandShell>
    </RegulatorGuard>
  );
}
