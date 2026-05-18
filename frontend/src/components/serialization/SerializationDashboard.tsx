"use client";

import { useEffect, useState } from "react";
import { GlassPanel } from "@/components/enterprise/GlassPanel";
import { fetchSerializationDashboard, fetchSerializationScanHistory } from "@/services/serialization-ops";

export function SerializationDashboard() {
  const [stats, setStats] = useState<Record<string, number> | null>(null);
  const [scans, setScans] = useState<unknown[]>([]);

  useEffect(() => {
    fetchSerializationDashboard()
      .then((r) => r.success && setStats(r.data as Record<string, number>))
      .catch(() => setStats(null));
    fetchSerializationScanHistory()
      .then((r) => r.success && setScans(r.data.scans ?? []))
      .catch(() => setScans([]));
  }, []);

  const tiles: [string, number | undefined][] = [
    ["Total serials", stats?.total_serials],
    ["With scans", stats?.serials_with_scans],
    ["Suspicious", stats?.suspicious_scan_events],
    ["Packaging units", stats?.packaging_units],
    ["Duplicate 24h", stats?.duplicate_scans_24h],
  ];

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        {tiles.map(([label, val]) => (
          <div key={label} className="glass-panel operational-glow rounded-xl border border-sovereign-800 p-4">
            <p className="text-[10px] uppercase tracking-wider text-slate-500">{label}</p>
            <p className="mt-2 text-2xl font-semibold tabular-nums text-white">
              {val != null ? val.toLocaleString() : "—"}
            </p>
          </div>
        ))}
      </div>
      <GlassPanel title="GS1 · QR · Barcode operations" subtitle="National serialization engine (Phase 10)">
        <ul className="grid gap-2 text-sm text-slate-400 md:grid-cols-2">
          <li>GS1 element strings on issuance</li>
          <li>Printable label payloads via API</li>
          <li>Carton / pallet packaging aggregation</li>
          <li>Serial scan history and replay protection</li>
          <li>Duplicate and suspicious scan detection</li>
          <li>Counterfeit probability escalation</li>
        </ul>
      </GlassPanel>
      <GlassPanel title="Recent scan history" subtitle="Live from /serialization/scan-history/">
        <ul className="max-h-64 space-y-2 overflow-y-auto text-xs">
          {scans.length === 0 && <li className="text-slate-600">No scans or connect with regulator JWT.</li>}
          {scans.map((s, i) => (
            <li key={i} className="rounded border border-sovereign-800 px-2 py-1 font-mono text-slate-300">
              {JSON.stringify(s)}
            </li>
          ))}
        </ul>
      </GlassPanel>
    </div>
  );
}
