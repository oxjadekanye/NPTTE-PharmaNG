"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchTraceabilityStory, type TraceabilityStory } from "@/services/traceability-demo";
import { GlassPanel } from "@/components/enterprise/GlassPanel";

const NODE_LABELS: Record<string, string> = {
  manufacturer: "Manufacturer",
  distributor: "Distributor",
  warehouse: "Warehouse",
  pharmacy: "Pharmacy",
  patient: "Patient",
};

export function TraceabilityLiveDemo({ showRegulatorLinks = true }: { showRegulatorLinks?: boolean }) {
  const [story, setStory] = useState<TraceabilityStory | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTraceabilityStory()
      .then((r) => setStory(r.data))
      .catch(() => setError("Demo story unavailable — run seed_traceability_demo on backend."));
  }, []);

  if (error) {
    return <p className="text-sm text-rose-300">{error}</p>;
  }

  if (!story) {
    return <p className="text-sm text-slate-500">Loading national traceability walkthrough…</p>;
  }

  if (!story.seeded) {
    return (
      <div className="rounded-xl border border-amber-500/40 bg-amber-500/10 p-4 text-sm text-amber-100">
        <p>{story.message}</p>
        <p className="mt-2 font-mono text-xs">python manage.py seed_traceability_demo</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <GlassPanel title="Medicine lifecycle" subtitle={story.product?.name ?? "TD demo product"}>
        <ol className="space-y-3">
          {(story.lifecycle_timeline ?? []).map((step) => (
            <li key={step.step} className="flex gap-3 text-sm">
              <span className="mt-0.5 h-2 w-2 shrink-0 rounded-full bg-sovereign-accent" />
              <span>
                <span className="font-medium text-slate-200">{step.label}</span>
                <span className="ml-2 text-xs uppercase text-emerald-400">{step.status}</span>
              </span>
            </li>
          ))}
        </ol>
      </GlassPanel>

      <GlassPanel title="Supply chain journey" subtitle="Manufacturer → patient">
        <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
          {["manufacturer", "distributor", "warehouse", "pharmacy", "patient"].map((node, i) => (
            <span key={node} className="flex items-center gap-2">
              <span className="rounded-lg border border-sovereign-700 bg-sovereign-950 px-2 py-1">
                {NODE_LABELS[node]}
              </span>
              {i < 4 && <span className="text-slate-600">→</span>}
            </span>
          ))}
        </div>
        <p className="mt-3 font-mono text-[10px] text-sovereign-accent">Hero serial: {story.hero_serial}</p>
      </GlassPanel>

      <div className="grid gap-4 lg:grid-cols-2">
        <GlassPanel title="Custody chain" subtitle="Sovereign ledger events">
          <ul className="max-h-48 space-y-1 overflow-y-auto font-mono text-[11px] text-slate-400">
            {(story.custody_chain ?? []).map((e, i) => (
              <li key={i}>
                {(e as { source_node?: string }).source_node} →{" "}
                {(e as { destination_node?: string }).destination_node}
              </li>
            ))}
          </ul>
        </GlassPanel>

        <GlassPanel title="Audit trail" subtitle="Regulatory + movement">
          <ul className="max-h-48 space-y-1 overflow-y-auto text-xs text-slate-400">
            {(story.regulatory_audits ?? []).map((a, i) => (
              <li key={i}>{(a as { action?: string }).action}</li>
            ))}
            {(story.transactions ?? []).slice(0, 5).map((t, i) => (
              <li key={`tx-${i}`}>{(t as { transaction_type?: string }).transaction_type}</li>
            ))}
          </ul>
        </GlassPanel>
      </div>

      {story.recall?.active && (
        <div className="rounded-xl border border-rose-500/50 bg-rose-500/10 px-4 py-3 text-sm text-rose-100">
          Recall active — batch {story.recall.batch_number}: {story.recall.reason}
        </div>
      )}

      {story.suspicious_scan && (
        <div className="rounded-xl border border-amber-500/50 bg-amber-500/10 px-4 py-3 text-sm text-amber-100">
          Suspicious scan example:{" "}
          <span className="font-mono">{story.suspicious_scan.serial}</span> — {story.suspicious_scan.note}
        </div>
      )}

      {showRegulatorLinks && (
        <p className="text-xs text-slate-500">
          Citizen test serials:{" "}
          <Link href="/citizen/demo-verify" className="text-sovereign-accent hover:underline">
            /citizen/demo-verify
          </Link>
        </p>
      )}
    </div>
  );
}
