"use client";

import { useEffect, useState } from "react";
import { fetchOperationalTasks } from "@/services/operations";

type TaskRow = {
  id: string;
  title: string;
  task_type: string;
  task_status: string;
  priority: string;
  due_at: string | null;
};

export function TaskPanel() {
  const [tasks, setTasks] = useState<TaskRow[]>([]);

  useEffect(() => {
    fetchOperationalTasks("open")
      .then((res) => setTasks((res.data?.tasks as TaskRow[]) ?? []))
      .catch(() => setTasks([]));
  }, []);

  if (tasks.length === 0) return null;

  return (
    <div className="rounded-xl border border-sovereign-800 bg-sovereign-900/50 p-4">
      <h3 className="text-sm font-semibold text-white">Operational tasks</h3>
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
