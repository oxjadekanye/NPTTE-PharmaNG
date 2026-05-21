"use client";

import { useEffect, useState } from "react";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { fetchOverdueTasks } from "@/services/operations";

export default function OverdueTasksPage() {
  const [tasks, setTasks] = useState<unknown[]>([]);

  useEffect(() => {
    fetchOverdueTasks().then((r) => setTasks(r.data?.tasks ?? []));
  }, []);

  return (
    <RegulatorGuard>
      <CommandShell title="Overdue tasks">
        <p className="mb-4 text-sm text-slate-400">Requires immediate field action</p>
        <ul className="space-y-2">
          {(tasks as { id: string; title: string; due_at?: string }[]).map((t) => (
            <li
              key={t.id}
              className="rounded-lg border border-amber-500/30 bg-amber-500/5 px-4 py-3 text-sm text-amber-50"
            >
              {t.title}
              {t.due_at && (
                <span className="ml-2 text-xs text-amber-200/80">
                  due {new Date(t.due_at).toLocaleString()}
                </span>
              )}
            </li>
          ))}
          {tasks.length === 0 && <p className="text-slate-500">No overdue tasks.</p>}
        </ul>
      </CommandShell>
    </RegulatorGuard>
  );
}
