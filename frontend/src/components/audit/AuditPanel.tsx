"use client";

import { AUDIT_LOG } from "@/demo/nigeria-intelligence";
import { useAuth } from "@/hooks/useAuth";

export function AuditPanel() {
  const { user } = useAuth();

  return (
    <div className="space-y-6">
      <p className="text-xs text-slate-500">
        Immutable audit timeline and access monitoring — simulated entries marked DEMO. Auth unchanged.
      </p>
      <div className="rounded-xl border border-sovereign-800 bg-sovereign-900/60 p-4">
        <h3 className="text-sm font-semibold text-white">Current session</h3>
        <p className="mt-2 text-sm text-slate-300">
          Role visibility: <span className="font-mono text-sovereign-accent">{user?.role_code ?? "—"}</span>
        </p>
        <p className="text-xs text-slate-500">User: {user?.username ?? "—"}</p>
      </div>
      <div className="rounded-xl border border-sovereign-800">
        <div className="border-b border-sovereign-800 px-4 py-3">
          <h3 className="text-sm font-semibold">Regulator action log (DEMO)</h3>
        </div>
        <ul className="divide-y divide-sovereign-800">
          {AUDIT_LOG.map((e) => (
            <li key={e.id} className="flex gap-4 px-4 py-3 text-sm">
              <time className="shrink-0 font-mono text-xs text-slate-500">
                {new Date(e.at).toLocaleString("en-NG")}
              </time>
              <div>
                <p className="text-slate-200">
                  <span className="text-sovereign-accent">{e.actor}</span> · {e.action}
                </p>
                <p className="text-xs text-slate-500">
                  {e.role} → {e.entity}
                  {e.immutable && (
                    <span className="ml-2 rounded bg-emerald-500/10 px-1 text-emerald-400">immutable</span>
                  )}
                </p>
              </div>
            </li>
          ))}
        </ul>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <SuspiciousActivityCard />
        <ChainOfCustodyCard />
      </div>
    </div>
  );
}

function SuspiciousActivityCard() {
  const items = [
    { at: "08:12", detail: "3 failed login attempts — IP Lagos (DEMO)" },
    { at: "07:55", detail: "Bulk export request — nptte_admin approved" },
  ];
  return (
    <div className="rounded-xl border border-amber-500/30 bg-amber-500/5 p-4">
      <h4 className="text-sm font-semibold text-amber-200">Suspicious activity monitoring</h4>
      <ul className="mt-3 space-y-2 text-xs text-amber-100/80">
        {items.map((i) => (
          <li key={i.at}>
            {i.at} — {i.detail}
          </li>
        ))}
      </ul>
    </div>
  );
}

function ChainOfCustodyCard() {
  return (
    <div className="rounded-xl border border-sovereign-800 bg-sovereign-900/60 p-4">
      <h4 className="text-sm font-semibold text-white">Chain of custody (DEMO)</h4>
      <ol className="mt-3 list-decimal space-y-1 pl-4 text-xs text-slate-400">
        <li>Sample sealed — Lagos Island 08:45</li>
        <li>Lab transfer — NAFDAC central lab</li>
        <li>Evidence locker — reference INC-2026-0142</li>
      </ol>
    </div>
  );
}
