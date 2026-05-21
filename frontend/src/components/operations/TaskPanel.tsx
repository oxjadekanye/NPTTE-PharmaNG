"use client";

import { memo, useEffect, useState } from "react";
import Link from "next/link";
import { fetchOperationalTasks } from "@/services/operations";

type TaskRow = {
  id: string;
  title: string;
  task_type: string;
  task_status: string;
  priority: string;
  due_at: string | null;
};

function TaskPanelInner() {
  const [tasks, setTasks] = useState<TaskRow[]>([]);

  useEffect(() => {
    fetchOperationalTasks()
      .then((res) => setTasks((res.data?.tasks as TaskRow[]) ?? []))
      .catch(() => setTasks([]));
  }, []);

  if (tasks.length === 0) return null;

  return (
    <div className="rounded-xl border border-sovereign-800 bg-sovereign-900/50 p-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-white">Operational tasks</h3>
        <Link href="/regulator/tasks" className="text-xs text-sky-400 hover:underline">
          View all
        </Link>
      </div>
      <ul className="mt-3 space-y-2">
        {tasks.slice(0, 5).map((t) => (
          <li key={t.id} className="rounded-lg border border-sovereign-700/60 px-3 py-2 text-xs">
            <p className="font-medium text-slate-200">{t.title}</p>
            <p className="text-slate-500">
              {t.task_type} · {t.priority}
              {t.due_at && ` · due ${new Date(t.due_at).toLocaleDateString()}`}
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
}

export const TaskPanel = memo(TaskPanelInner);
