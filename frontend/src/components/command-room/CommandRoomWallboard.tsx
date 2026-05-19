"use client";

import { useCallback, useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { fetchCommandRoomSnapshot, fetchTaskOrchestration } from "@/services/command-orchestration";
import { useRealtimePatches } from "@/hooks/useRealtimePatches";
import { LiveEventFeed } from "@/components/realtime/LiveEventFeed";

const OperationalMap = dynamic(
  () => import("@/components/maps/OperationalMap").then((m) => m.OperationalMap),
  { ssr: false, loading: () => <div className="h-[360px] animate-pulse rounded-xl bg-sovereign-900" /> }
);

export function CommandRoomWallboard() {
  const [snapshot, setSnapshot] = useState<Record<string, unknown> | null>(null);
  const [tasks, setTasks] = useState<Record<string, unknown> | null>(null);
  const { patches, metrics } = useRealtimePatches(true, "national");

  const refresh = useCallback(async () => {
    const [room, taskRes] = await Promise.all([fetchCommandRoomSnapshot(), fetchTaskOrchestration()]);
    if (room.success) setSnapshot(room.data);
    if (taskRes.success) setTasks(taskRes.data);
  }, []);

  useEffect(() => {
    void refresh();
    const id = setInterval(() => void refresh(), 20000);
    return () => clearInterval(id);
  }, [refresh]);

  const readiness =
    Number(metrics.national_threat?.delta_suspicious ?? 0) > 0
      ? Number(snapshot?.national_readiness_index ?? 70) - 2
      : snapshot?.national_readiness_index ?? "—";

  const openCases = (snapshot?.open_cases as Record<string, unknown>[]) ?? [];
  const opTasks = (tasks?.tasks as Record<string, unknown>[]) ?? [];
  const escalations = patches.filter((p) => p.scope === "investigation" || p.scope === "channel").slice(0, 6);

  return (
    <div className="min-h-screen bg-black text-slate-100">
      <header className="border-b border-sovereign-800 px-6 py-4">
        <p className="text-xs uppercase tracking-[0.2em] text-sovereign-accent">NPTTE Command Room</p>
        <h1 className="text-2xl font-semibold text-white">National operational wallboard</h1>
        <p className="text-xs text-slate-500">Live streambus · patch updates · auto-refresh 20s</p>
      </header>

      <div className="grid gap-4 p-4 xl:grid-cols-12">
        <section className="xl:col-span-8">
          <div className="h-[360px] overflow-hidden rounded-xl border border-sovereign-800">
            <OperationalMap layer="operational" heightClass="h-[360px]" />
          </div>
        </section>
        <section className="space-y-3 xl:col-span-4">
          <div className="rounded-xl border border-sovereign-800 bg-sovereign-950 p-4">
            <p className="text-[10px] uppercase text-slate-500">National readiness</p>
            <p className="text-4xl font-semibold tabular-nums text-emerald-400">{String(readiness)}</p>
          </div>
          <div className="rounded-xl border border-amber-500/30 bg-amber-500/5 p-3 text-xs">
            <p className="font-semibold text-amber-200">AI briefing ticker</p>
            <p className="mt-1 text-slate-400">Use Executive AI briefing — manual trigger only.</p>
          </div>
          <div className="max-h-48 overflow-y-auto rounded-xl border border-sovereign-800 p-3">
            <p className="mb-2 text-[10px] uppercase text-slate-500">Live patches ({patches.length})</p>
            {escalations.map((p, i) => (
              <p key={`${p.target}-${i}`} className="text-[11px] text-slate-400">
                [{p.scope}] {p.target}
              </p>
            ))}
          </div>
        </section>

        <section className="xl:col-span-4">
          <div className="rounded-xl border border-sovereign-800 p-3">
            <h2 className="text-xs font-semibold uppercase text-slate-400">Streambus feed</h2>
            <div className="mt-2 max-h-64">
              <LiveEventFeed />
            </div>
          </div>
        </section>
        <section className="xl:col-span-4">
          <div className="rounded-xl border border-sovereign-800 p-3">
            <h2 className="text-xs font-semibold uppercase text-slate-400">Open investigations</h2>
            <ul className="mt-2 max-h-64 space-y-1 overflow-y-auto text-xs">
              {openCases.map((c) => (
                <li key={String(c.id)} className="text-slate-300">
                  {String(c.title)} · {String(c.severity)}
                </li>
              ))}
            </ul>
          </div>
        </section>
        <section className="xl:col-span-4">
          <div className="rounded-xl border border-sovereign-800 p-3">
            <h2 className="text-xs font-semibold uppercase text-slate-400">Operational tasks</h2>
            <ul className="mt-2 max-h-64 space-y-1 overflow-y-auto text-xs">
              {opTasks.map((t) => (
                <li key={String(t.id)} className={t.overdue ? "text-red-300" : "text-slate-300"}>
                  {String(t.title)}
                  {t.overdue ? " · OVERDUE" : ""}
                </li>
              ))}
            </ul>
          </div>
        </section>
      </div>
    </div>
  );
}
