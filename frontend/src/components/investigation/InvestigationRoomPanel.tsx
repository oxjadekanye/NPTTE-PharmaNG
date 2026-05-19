"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { fetchInvestigationRoom, postInvestigationRoom } from "@/services/command-orchestration";
import { EnforcementCopilotPanel } from "@/components/copilot/EnforcementCopilotPanel";

export function InvestigationRoomPanel({ caseId }: { caseId: string }) {
  const [room, setRoom] = useState<Record<string, unknown> | null>(null);
  const [note, setNote] = useState("");
  const [msg, setMsg] = useState<string | null>(null);

  const load = useCallback(async () => {
    const res = await fetchInvestigationRoom(caseId);
    if (res.success) setRoom(res.data);
  }, [caseId]);

  useEffect(() => {
    void load();
    const id = setInterval(() => void load(), 15000);
    return () => clearInterval(id);
  }, [load]);

  const caseInfo = (room?.case as Record<string, unknown>) ?? {};
  const notes = (room?.notes as Record<string, unknown>[]) ?? [];
  const comments = (room?.comments as Record<string, unknown>[]) ?? [];
  const feed = (room?.activity_feed as Record<string, unknown>[]) ?? [];

  const addNote = async () => {
    if (!note.trim()) return;
    const res = await postInvestigationRoom(caseId, { action: "note", body: note });
    if (res.success) {
      setNote("");
      setMsg("Note added");
      void load();
    }
  };

  return (
    <div className="space-y-4">
      <Link href="/regulator/enforcement/cases" className="text-xs text-sovereign-accent hover:underline">
        ← Cases
      </Link>
      <header className="rounded-xl border border-sovereign-800 p-4">
        <p className="text-xs text-slate-500">{String(caseInfo.case_reference)}</p>
        <h1 className="text-lg font-semibold text-white">{String(caseInfo.title)}</h1>
        <p className="text-sm text-slate-400">
          {String(caseInfo.case_status)} · {String(caseInfo.severity)}
        </p>
      </header>

      <div className="grid gap-4 lg:grid-cols-2">
        <section className="rounded-xl border border-sovereign-800 p-3">
          <h2 className="text-xs font-semibold uppercase text-slate-400">Live activity feed</h2>
          <ul className="mt-2 max-h-64 space-y-2 overflow-y-auto text-xs text-slate-300">
            {feed.map((e, i) => (
              <li key={String(e.id ?? i)} className="rounded border border-sovereign-800/50 p-2">
                [{String(e.entry_type)}] {String(e.summary)}
              </li>
            ))}
          </ul>
        </section>
        <section className="rounded-xl border border-sovereign-800 p-3">
          <h2 className="text-xs font-semibold uppercase text-slate-400">Investigation notes</h2>
          <ul className="mt-2 max-h-40 space-y-1 overflow-y-auto text-xs text-slate-400">
            {notes.map((n) => (
              <li key={String(n.id)}>
                {String(n.author)}: {String(n.body)}
              </li>
            ))}
          </ul>
          <textarea
            className="mt-2 w-full rounded border border-sovereign-700 bg-sovereign-950 p-2 text-xs text-slate-200"
            rows={3}
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="Add investigation note…"
          />
          <button
            type="button"
            onClick={() => void addNote()}
            className="mt-2 rounded border border-sovereign-600 px-3 py-1 text-xs text-sovereign-accent"
          >
            Post note
          </button>
          {msg && <p className="mt-1 text-emerald-400">{msg}</p>}
        </section>
      </div>

      <section className="rounded-xl border border-sovereign-800 p-3">
        <h2 className="text-xs font-semibold uppercase text-slate-400">Collaboration comments</h2>
        <ul className="mt-2 space-y-1 text-xs text-slate-400">
          {comments.map((c) => (
            <li key={String(c.id)}>
              {String(c.author)} (L{String(c.escalation_level)}): {String(c.body)}
            </li>
          ))}
        </ul>
      </section>

      <EnforcementCopilotPanel caseId={caseId} />
    </div>
  );
}
