"use client";

import { useState } from "react";
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
        {timeline.map((t, i) => (
          <li key={i} className="relative text-sm text-slate-300">
            <span className="absolute -left-[1.15rem] top-1 h-2 w-2 rounded-full bg-emerald-400 scan-pulse" />
            <pre className="whitespace-pre-wrap font-mono text-[10px] text-slate-500">
              {JSON.stringify(t, null, 2)}
            </pre>
          </li>
        ))}
        {timeline.length === 0 && (
          <li className="text-slate-600">Enter a serial to view sovereign custody chain.</li>
        )}
      </ol>
    </div>
  );
}
