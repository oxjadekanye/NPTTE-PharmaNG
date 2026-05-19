"use client";

import { useState } from "react";
import { humanLabel, formatTimestamp } from "@/services/explorer-format";
import { fetchCustodyTimeline } from "@/services/custody";

export function CustodyTimeline() {
  const [serial, setSerial] = useState("");
  const [timeline, setTimeline] = useState<unknown[]>([]);
  const [error, setError] = useState("");

  async function load() {
    setError("");
    try {
      const r = await fetchCustodyTimeline(serial);
      setTimeline(r.data.timeline ?? []);
    } catch {
      setError("Unable to load custody timeline.");
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <input
          className="min-w-[200px] flex-1 rounded-lg border border-sovereign-700 bg-sovereign-950 px-3 py-2 font-mono text-sm"
          placeholder="NG-NPTTE-…"
          value={serial}
          onChange={(e) => setSerial(e.target.value)}
        />
        <button
          type="button"
          onClick={load}
          className="rounded-lg bg-sovereign-accent/20 px-4 py-2 text-sm text-sovereign-accent"
        >
          Load chain
        </button>
      </div>
      {error && <p className="text-sm text-rose-300">{error}</p>}
      <ol className="space-y-3 border-l border-sovereign-700 pl-4">
        {timeline.map((t, i) => {
          const row = (t && typeof t === "object" ? t : {}) as Record<string, unknown>;
          return (
            <li key={i} className="relative text-sm text-slate-300">
              <span className="absolute -left-[1.15rem] top-1 h-2 w-2 rounded-full bg-emerald-400 scan-pulse" />
              <p className="font-medium text-slate-200">{String(row.event_type ?? row.status ?? "Custody event")}</p>
              <p className="text-[10px] text-slate-500">
                {row.timestamp ? formatTimestamp(String(row.timestamp)) : ""}
                {row.location ? ` · ${String(row.location)}` : ""}
              </p>
              {row.actor ? <p className="text-[10px] text-slate-600">{humanLabel("actor")}: {String(row.actor)}</p> : null}
            </li>
          );
        })}
        {timeline.length === 0 && (
          <li className="text-slate-600">Enter a serial to view sovereign custody chain.</li>
        )}
      </ol>
    </div>
  );
}
