"use client";

import { memo, useEffect, useState } from "react";
import Link from "next/link";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { OperationalSkeleton } from "@/components/ui/OperationalSkeleton";
import { useRealtimeFeed } from "@/hooks/useRealtimeFeed";
import { fetchOperationalTasks, fetchOverdueTasks } from "@/services/operations";

type TaskRow = {
  id: string;
  title: string;
  task_type: string;
  task_status: string;
  priority: string;
  due_at: string | null;
  escalation_status?: string;
};

function TasksDashboardInner() {
  const [tasks, setTasks] = useState<TaskRow[]>([]);
  const [overdue, setOverdue] = useState<TaskRow[]>([]);
  const [loading, setLoading] = useState(true);
  const { feed, refresh: refreshFeed } = useRealtimeFeed({ channels: "operational_task,task" });

  useEffect(() => {
    Promise.all([fetchOperationalTasks(), fetchOverdueTasks()])
      .then(([open, od]) => {
        setTasks((open.data?.tasks as TaskRow[]) ?? []);
        setOverdue((od.data?.tasks as TaskRow[]) ?? []);
      })
      .finally(() => setLoading(false));
  }, [feed?.polled_at]);

  return (
    <CommandShell title="Operational tasks" subtitle="National field assignment queue">
      <div className="mb-4 flex flex-wrap gap-2">
        <Link
          href="/regulator/tasks/overdue"
          className="rounded-lg border border-amber-500/40 bg-amber-500/10 px-3 py-2 text-xs text-amber-100"
        >
          Overdue ({overdue.length})
        </Link>
        <Link
          href="/regulator/tasks/calendar"
          className="rounded-lg border border-sovereign-700 px-3 py-2 text-xs text-slate-300"
        >
          Calendar
        </Link>
        <button
          type="button"
          onClick={() => void refreshFeed(true)}
          className="rounded-lg border border-sky-500/40 bg-sky-500/10 px-3 py-2 text-xs text-sky-100"
        >
          Refresh feed
        </button>
      </div>
      {loading ? (
        <OperationalSkeleton rows={6} />
      ) : (
        <div className="grid gap-3 md:grid-cols-2">
          {tasks.map((t) => (
            <article
              key={t.id}
              className="rounded-xl border border-sovereign-800 bg-sovereign-900/60 p-4 transition hover:border-sky-500/40"
            >
              <h3 className="font-semibold text-white">{t.title}</h3>
              <p className="mt-1 text-xs text-slate-400">
                {t.task_type} · {t.priority} · {t.task_status}
                {t.escalation_status === "escalated" && " · ESCALATED"}
              </p>
              {t.due_at && (
                <p className="mt-2 text-xs text-slate-500">Due {new Date(t.due_at).toLocaleString()}</p>
              )}
            </article>
          ))}
          {tasks.length === 0 && (
            <p className="text-sm text-slate-500">No open tasks — create via operations API or explorer actions.</p>
          )}
        </div>
      )}
    </CommandShell>
  );
}

const TasksDashboard = memo(TasksDashboardInner);

export default function TasksPage() {
  return (
    <RegulatorGuard>
      <TasksDashboard />
    </RegulatorGuard>
  );
}
