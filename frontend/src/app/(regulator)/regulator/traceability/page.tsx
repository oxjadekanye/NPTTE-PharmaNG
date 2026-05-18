"use client";

import { useEffect, useState } from "react";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { DemoBadge } from "@/components/command/DemoBadge";
import {
  approveBatch,
  fetchBatchAuditTrail,
  fetchPendingBatches,
  fetchRecallAffected,
  fetchTraceabilityTransactions,
  recallBatch,
  rejectBatch,
  regulatorVerifyLookup,
} from "@/services/traceability";

type Tab = "queue" | "serialization" | "recall" | "verify" | "timeline";

export default function RegulatorTraceabilityPage() {
  const [tab, setTab] = useState<Tab>("queue");
  const [pending, setPending] = useState<unknown[]>([]);
  const [lookupSerial, setLookupSerial] = useState("");
  const [lookupResult, setLookupResult] = useState<Record<string, unknown> | null>(null);
  const [timeline, setTimeline] = useState<unknown[]>([]);
  const [audit, setAudit] = useState<unknown[]>([]);
  const [selectedBatch, setSelectedBatch] = useState<string | null>(null);
  const [affected, setAffected] = useState<string[]>([]);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    if (tab === "queue") {
      fetchPendingBatches()
        .then((rows) => setPending(rows))
        .catch(() => setErr("Could not load pending batches (check auth)."));
    }
    if (tab === "timeline") {
      fetchTraceabilityTransactions()
        .then((rows) => setTimeline(rows.slice(0, 40)))
        .catch(() => setErr("Could not load transactions."));
    }
    if (tab === "recall" && selectedBatch) {
      fetchRecallAffected(selectedBatch)
        .then((r) => setAffected(r.data?.pharmacy_organisation_ids ?? []))
        .catch(() => setAffected([]));
    }
    if (selectedBatch && tab === "queue") {
      fetchBatchAuditTrail(selectedBatch)
        .then((rows) => setAudit(rows))
        .catch(() => setAudit([]));
    }
  }, [tab, selectedBatch]);

  return (
    <RegulatorGuard>
      <CommandShell title="Traceability & Serialization">
        <div className="mb-4 flex flex-wrap items-center gap-3">
          <DemoBadge />
          <p className="text-xs text-slate-500">
            Phase 8 panels — uses live regulatory APIs when authenticated. Empty states are normal on a fresh database.
          </p>
        </div>
        {err && <p className="mb-4 text-sm text-amber-400">{err}</p>}
        <div className="mb-6 flex flex-wrap gap-2 border-b border-sovereign-800 pb-4">
          {(
            [
              ["queue", "Batch approval queue"],
              ["serialization", "Serialization console"],
              ["recall", "Recall management"],
              ["verify", "Verification lookup"],
              ["timeline", "Movement timeline"],
            ] as const
          ).map(([id, label]) => (
            <button
              key={id}
              type="button"
              onClick={() => {
                setTab(id);
                setErr(null);
              }}
              className={`rounded-lg px-3 py-1.5 text-sm font-medium transition ${
                tab === id ? "bg-sovereign-accent text-white" : "text-slate-400 hover:bg-sovereign-800 hover:text-white"
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        {tab === "queue" && (
          <div className="grid gap-6 lg:grid-cols-2">
            <div className="rounded-xl border border-sovereign-800 bg-sovereign-900/50 p-4">
              <h3 className="text-sm font-semibold text-white">Pending batches</h3>
              <ul className="mt-3 max-h-80 space-y-2 overflow-y-auto text-sm">
                {pending.length === 0 ? (
                  <li className="text-slate-500">No pending batches</li>
                ) : (
                  pending.map((b: unknown) => {
                    const row = b as Record<string, unknown>;
                    const id = String(row.id ?? "");
                    return (
                      <li key={id}>
                        <button
                          type="button"
                          className={`w-full rounded border px-2 py-2 text-left ${
                            selectedBatch === id ? "border-sovereign-accent bg-sovereign-accent/10" : "border-sovereign-800"
                          }`}
                          onClick={() => setSelectedBatch(id)}
                        >
                          <span className="font-mono text-xs">{String(row.batch_number)}</span>
                          <span className="ml-2 text-slate-400">{String(row.lifecycle_status ?? "")}</span>
                        </button>
                      </li>
                    );
                  })
                )}
              </ul>
              {selectedBatch && (
                <div className="mt-4 flex flex-wrap gap-2">
                  <button
                    type="button"
                    className="rounded bg-emerald-700 px-3 py-1.5 text-xs text-white"
                    onClick={() => approveBatch(selectedBatch).then(() => setTab("queue"))}
                  >
                    Approve
                  </button>
                  <button
                    type="button"
                    className="rounded bg-amber-700 px-3 py-1.5 text-xs text-white"
                    onClick={() => {
                      const reason = window.prompt("Reject reason?");
                      if (reason) rejectBatch(selectedBatch, reason).then(() => setTab("queue"));
                    }}
                  >
                    Reject
                  </button>
                </div>
              )}
            </div>
            <div className="rounded-xl border border-sovereign-800 bg-sovereign-900/50 p-4">
              <h3 className="text-sm font-semibold text-white">Audit trail</h3>
              <pre className="mt-2 max-h-80 overflow-auto text-xs text-slate-400">
                {JSON.stringify(audit, null, 2)}
              </pre>
            </div>
          </div>
        )}

        {tab === "serialization" && (
          <div className="rounded-xl border border-sovereign-800 bg-sovereign-900/50 p-6 text-sm text-slate-300">
            <p>
              Manufacturers register products and batches via{" "}
              <code className="text-sovereign-accent">POST /api/v1/manufacturers/products/register/</code> and{" "}
              <code className="text-sovereign-accent">POST /api/v1/manufacturers/batches/create/</code>, then{" "}
              <code className="text-sovereign-accent">submit-for-approval</code> and{" "}
              <code className="text-sovereign-accent">generate-serials</code> after NAFDAC approval.
            </p>
            <p className="mt-3 text-xs text-slate-500">
              Serial format: NG-NPTTE-{"{PRODUCTCODE}"}-{"{YEAR}"}-{"{SEQUENCE}"} — set{" "}
              <code>national_product_code</code> on the product for stable codes.
            </p>
          </div>
        )}

        {tab === "recall" && (
          <div className="space-y-4">
            <input
              className="w-full max-w-md rounded border border-sovereign-700 bg-sovereign-950 px-3 py-2 font-mono text-sm"
              placeholder="Batch UUID"
              value={selectedBatch ?? ""}
              onChange={(e) => setSelectedBatch(e.target.value || null)}
            />
            <button
              type="button"
              className="rounded bg-red-800 px-4 py-2 text-sm text-white"
              onClick={() => {
                const reason = window.prompt("Recall reason?");
                if (selectedBatch && reason) recallBatch(selectedBatch, reason).then(() => setTab("recall"));
              }}
            >
              Issue national recall
            </button>
            <p className="text-xs text-slate-500">Affected pharmacy organisation IDs (stock on hand):</p>
            <pre className="rounded border border-sovereign-800 bg-sovereign-950 p-3 text-xs text-slate-400">
              {JSON.stringify(affected, null, 2)}
            </pre>
          </div>
        )}

        {tab === "verify" && (
          <div className="max-w-xl space-y-4">
            <input
              className="w-full rounded border border-sovereign-700 bg-sovereign-950 px-3 py-2 font-mono text-sm"
              placeholder="Serial number"
              value={lookupSerial}
              onChange={(e) => setLookupSerial(e.target.value)}
            />
            <button
              type="button"
              className="rounded bg-sovereign-accent px-4 py-2 text-sm text-white"
              onClick={() =>
                regulatorVerifyLookup(lookupSerial).then((r) => setLookupResult(r.data as Record<string, unknown>))
              }
            >
              Regulator lookup
            </button>
            {lookupResult && (
              <pre className="rounded border border-sovereign-800 bg-sovereign-950 p-3 text-xs text-slate-300">
                {JSON.stringify(lookupResult, null, 2)}
              </pre>
            )}
          </div>
        )}

        {tab === "timeline" && (
          <pre className="max-h-[480px] overflow-auto rounded-xl border border-sovereign-800 bg-sovereign-950 p-4 text-xs text-slate-400">
            {JSON.stringify(timeline, null, 2)}
          </pre>
        )}
      </CommandShell>
    </RegulatorGuard>
  );
}
