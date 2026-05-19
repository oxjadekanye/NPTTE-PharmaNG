"use client";

import { useCommandStore } from "@/store/command-store";
import { useExplorerDrawerStore } from "@/store/explorer-drawer-store";

export function ActivityLog() {
  const log = useCommandStore((s) => s.activityLog);
  const openDrawer = useExplorerDrawerStore((s) => s.openDrawer);

  return (
    <div className="rounded-xl border border-sovereign-800 bg-sovereign-900/60 p-4">
      <button
        type="button"
        className="mb-3 w-full text-left"
        onClick={() =>
          openDrawer({
            entityType: "task",
            entityId: "command-activity-current",
            title: "Command activity",
          })
        }
      >
        <h3 className="text-sm font-semibold text-white hover:text-sovereign-accent">Command activity</h3>
        <p className="text-[10px] text-slate-500">Simulated operational log (DEMO) · click header for trace</p>
      </button>
      <ul className="max-h-40 space-y-1 overflow-y-auto font-mono text-xs text-slate-400">
        {log.map((line, i) => (
          <li key={`${line}-${i}`}>
            <button
              type="button"
              className="w-full rounded px-1 text-left hover:bg-sovereign-800/60 hover:text-slate-200"
              onClick={() =>
                openDrawer({
                  entityType: "task",
                  entityId: "command-activity-current",
                  title: line.slice(0, 80),
                })
              }
            >
              {line}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
