"use client";

import { useState } from "react";
import Link from "next/link";
import { MobileScanWorkflow } from "@/components/scanning/MobileScanWorkflow";
import { fetchScanHistory, type ScanIngestResult } from "@/services/scanning";
import { GlassPanel } from "@/components/enterprise/GlassPanel";

const CHECKLIST = [
  "Storage conditions documented",
  "Serialisation labels intact",
  "Custody records match physical stock",
  "Recall notices displayed",
  "Licensed premises verification",
];

export default function FieldInspectionPage() {
  const [checks, setChecks] = useState<Record<string, boolean>>({});
  const [siteRisk, setSiteRisk] = useState(42);
  const [history, setHistory] = useState<ScanIngestResult[]>([]);
  const [enforcementNote, setEnforcementNote] = useState("");

  async function loadHistory(serial?: string) {
    try {
      const res = await fetchScanHistory(serial);
      setHistory(res.data.scans);
      if (res.data.scans.length) {
        const avg =
          res.data.scans.reduce((a, s) => a + s.risk_score, 0) / res.data.scans.length;
        setSiteRisk(Math.min(99, Math.round(avg + 20)));
      }
    } catch {
      setHistory([]);
    }
  }

  return (
    <div className="min-h-screen bg-sovereign-950 text-slate-100">
      <div className="border-b border-sovereign-800 px-4 py-4 sm:px-6">
        <Link href="/regulator" className="text-[10px] uppercase tracking-widest text-sovereign-accent">
          ← Regulator console
        </Link>
        <h1 className="mt-2 text-xl font-semibold">Field inspection mode</h1>
        <p className="text-xs text-slate-500">On-site checklist, evidence capture, and serial scans.</p>
      </div>

      <div className="grid gap-6 p-4 lg:grid-cols-2 lg:p-6">
        <GlassPanel title="Inspection checklist" subtitle="Mark items observed on site">
          <ul className="space-y-2 text-sm">
            {CHECKLIST.map((item) => (
              <li key={item} className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={!!checks[item]}
                  onChange={() => setChecks((c) => ({ ...c, [item]: !c[item] }))}
                  className="rounded border-sovereign-600"
                />
                <span>{item}</span>
              </li>
            ))}
          </ul>
          <p className="mt-4 text-xs text-slate-500">
            Site risk score (derived): <span className="font-mono text-sovereign-accent">{siteRisk}</span>
          </p>
        </GlassPanel>

        <GlassPanel title="Evidence placeholder" subtitle="Attach photos in production build">
          <div className="flex h-32 items-center justify-center rounded-lg border border-dashed border-sovereign-700 text-xs text-slate-500">
            Camera / file upload — pilot placeholder
          </div>
        </GlassPanel>

        <div className="lg:col-span-2">
          <MobileScanWorkflow
            title="Inspection scan"
            subtitle="Scan unit serials during NAFDAC field visit."
            scanType="regulator_inspection"
            actorRole="regulator"
            backHref="/regulator/field-inspection"
          />
        </div>

        <GlassPanel title="Scan history" subtitle="Recent serials at this site">
          <button
            type="button"
            onClick={() => loadHistory()}
            className="mb-3 rounded border border-sovereign-700 px-2 py-1 text-xs"
          >
            Refresh history
          </button>
          <ul className="max-h-40 space-y-1 overflow-y-auto text-xs font-mono text-slate-400">
            {history.map((h) => (
              <li key={h.id}>
                {h.serial_number} — {h.outcome_label}
              </li>
            ))}
            {!history.length && <li>No scans loaded</li>}
          </ul>
        </GlassPanel>

        <GlassPanel title="Enforcement action" subtitle="Placeholder for formal action record">
          <textarea
            value={enforcementNote}
            onChange={(e) => setEnforcementNote(e.target.value)}
            placeholder="Seizure notice, warning letter reference…"
            className="h-24 w-full rounded-lg border border-sovereign-700 bg-sovereign-950 px-3 py-2 text-sm"
          />
        </GlassPanel>
      </div>
    </div>
  );
}
