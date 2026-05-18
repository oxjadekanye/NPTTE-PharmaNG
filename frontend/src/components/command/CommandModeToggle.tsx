"use client";

import clsx from "clsx";
import { useCommandStore } from "@/store/command-store";

export function CommandModeToggle() {
  const mode = useCommandStore((s) => s.mode);
  const setMode = useCommandStore((s) => s.setMode);

  return (
    <div className="flex rounded-lg border border-sovereign-700 bg-sovereign-900/90 p-0.5 text-xs">
      <button
        type="button"
        onClick={() => setMode("operational")}
        className={clsx(
          "rounded-md px-3 py-1.5 font-medium transition",
          mode === "operational"
            ? "bg-sovereign-accent text-white shadow"
            : "text-slate-400 hover:text-white"
        )}
      >
        Operational Command
      </button>
      <button
        type="button"
        onClick={() => setMode("ministerial")}
        className={clsx(
          "rounded-md px-3 py-1.5 font-medium transition",
          mode === "ministerial"
            ? "bg-emerald-700 text-white shadow"
            : "text-slate-400 hover:text-white"
        )}
      >
        Ministerial Overview
      </button>
    </div>
  );
}
