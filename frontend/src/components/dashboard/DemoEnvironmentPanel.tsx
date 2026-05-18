"use client";

import { DEMO_ENTITIES } from "@/demo/demo-entities";

export function DemoEnvironmentPanel() {
  return (
    <div className="rounded-xl border border-sovereign-800 bg-sovereign-900/50 p-5">
      <h3 className="text-sm font-semibold text-white">National demo environment</h3>
      <p className="mt-1 text-[10px] text-slate-500">
        Simulated entities across Nigeria — not production operational records
      </p>
      <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {DEMO_ENTITIES.map((group) => (
          <div key={group.category} className="rounded-lg border border-sovereign-800/80 bg-sovereign-950/40 p-3">
            <p className="text-xs font-medium uppercase text-sovereign-accent">{group.category}</p>
            <ul className="mt-2 max-h-24 overflow-y-auto text-xs text-slate-400">
              {group.items.slice(0, 5).map((item) => (
                <li key={item} className="truncate">
                  {item}
                </li>
              ))}
              {group.items.length > 5 && (
                <li className="text-slate-600">+{group.items.length - 5} more…</li>
              )}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
