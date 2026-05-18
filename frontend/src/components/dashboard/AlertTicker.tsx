"use client";

import { useCommandStore } from "@/store/command-store";

export function AlertTicker() {
  const message = useCommandStore((s) => s.ticker[0] ?? "");

  return (
    <div className="overflow-hidden rounded-lg border border-red-500/30 bg-red-950/40">
      <div className="flex items-center gap-3 px-4 py-2">
        <span className="shrink-0 rounded bg-red-500/20 px-2 py-0.5 text-[10px] font-bold uppercase text-red-300">
          Alert
        </span>
        <p className="animate-pulse truncate text-sm text-red-100" key={message}>
          {message}
        </p>
      </div>
    </div>
  );
}
