"use client";

import { useEffect, useState } from "react";
import clsx from "clsx";
import { useRealtime } from "@/hooks/useRealtime";
import { fetchCommandCenterLive } from "@/services/streambus";
import { useExplorerDrawerStore } from "@/store/explorer-drawer-store";

type LiveEvent = {
  event_id?: string;
  event_type?: string;
  payload?: Record<string, unknown>;
  sequence_number?: number;
};

export function LiveEventFeed({ useSse = true }: { useSse?: boolean }) {
  const { messages, connected } = useRealtime(useSse);
  const [events, setEvents] = useState<LiveEvent[]>([]);
  const [telemetry, setTelemetry] = useState<Record<string, number>>({});
  const openDrawer = useExplorerDrawerStore((s) => s.openDrawer);

  useEffect(() => {
    const load = () =>
      fetchCommandCenterLive()
        .then((r) => {
          setEvents((r.data?.events as LiveEvent[]) ?? []);
          setTelemetry(r.data?.telemetry ?? {});
        })
        .catch(() => {});
    load();
    const t = setInterval(load, 15000);
    return () => clearInterval(t);
  }, []);

  const sseEvents = messages
    .filter((m) => m.type === "event")
    .map((m) => (m.payload as LiveEvent) ?? {})
    .slice(0, 20);

  const merged = [...sseEvents, ...events].slice(0, 25);

  return (
    <div className="rounded-xl border border-sovereign-800 bg-sovereign-900/60 p-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-white">Live operational stream</h3>
          <span
            className={clsx(
              "inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-[10px]",
              connected ? "bg-emerald-500/20 text-emerald-300" : "bg-slate-700 text-slate-400"
            )}
          >
            <span
              className={clsx("h-1.5 w-1.5 rounded-full", connected ? "animate-pulse bg-emerald-400" : "bg-slate-500")}
            />
            {connected ? "SSE live" : "Polling"}
          </span>
        </div>
        <div className="mt-3 grid grid-cols-3 gap-2 text-center text-[10px]">
          <button
            type="button"
            className="rounded-lg border border-sovereign-700/60 py-2 outline-none transition hover:bg-sovereign-800/50"
            onClick={() =>
              openDrawer({ entityType: "national_risk", entityId: "national-risk-current", title: "Scan throughput" })
            }
          >
            <p className="text-slate-500">Scans/hr</p>
            <p className="text-lg font-semibold text-white">{telemetry.scan_throughput ?? "—"}</p>
          </button>
          <button
            type="button"
            className="rounded-lg border border-sovereign-700/60 py-2 outline-none transition hover:bg-sovereign-800/50"
            onClick={() =>
              openDrawer({ entityType: "national_risk", entityId: "national-risk-current", title: "Event throughput" })
            }
          >
            <p className="text-slate-500">Events/hr</p>
            <p className="text-lg font-semibold text-white">{telemetry.event_throughput ?? "—"}</p>
          </button>
          <button
            type="button"
            className="rounded-lg border border-amber-500/30 py-2 outline-none transition hover:bg-amber-500/10"
            onClick={() =>
              openDrawer({
                entityType: "national_risk",
                entityId: "counterfeit-detections-current",
                title: "Suspicious rate",
              })
            }
          >
            <p className="text-amber-400/80">Suspicious %</p>
            <p className="text-lg font-semibold text-amber-300">
              {typeof telemetry.suspicious_rate === "number" ? telemetry.suspicious_rate.toFixed(1) : "—"}
            </p>
          </button>
        </div>
        <ul className="mt-4 max-h-64 space-y-2 overflow-y-auto">
          {merged.length === 0 && <li className="text-xs text-slate-500">Waiting for events…</li>}
          {merged.map((ev, i) => (
            <li
              key={ev.event_id ?? `ev-${i}`}
              className="rounded-lg border border-sovereign-700/50 px-3 py-2 text-xs"
            >
              <button
                type="button"
                className="w-full text-left outline-none transition hover:text-sovereign-accent"
                onClick={() =>
                  openDrawer({
                    entityType: "national_risk",
                    entityId: "national-risk-current",
                    title: String(ev.event_type ?? "stream event"),
                  })
                }
              >
                <p className="font-medium text-slate-200">{ev.event_type ?? "event"}</p>
                <p className="text-slate-500">#{ev.sequence_number ?? "—"}</p>
              </button>
            </li>
          ))}
        </ul>
      </div>
  );
}
