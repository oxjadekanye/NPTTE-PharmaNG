"use client";

import type { ScanIngestResult, ScanType } from "@/services/scanning";

const OUTCOME_LABELS: Record<ScanType, Record<string, string>> = {
  citizen_verify: {
    authentic: "Authentic",
    suspicious: "Suspicious",
    recalled: "Recalled",
    expired: "Expired",
    duplicate_scan: "Duplicate scan",
    invalid_serial: "Invalid serial",
    queued: "Queued",
  },
  pharmacy_receive: {
    received: "Received",
    dispensed: "Dispensed",
    quarantined: "Quarantined",
    queued: "Queued",
  },
  pharmacy_dispense: {
    dispensed: "Dispensed",
    quarantined: "Quarantined",
    received: "Received",
    queued: "Queued",
  },
  regulator_inspection: {
    inspection_passed: "Inspection passed",
    flagged: "Flagged",
    seized: "Seized",
    queued: "Queued",
  },
  customs_verify: {
    import_verified: "Import verified",
    held: "Held",
    suspicious: "Suspicious",
    queued: "Queued",
  },
  warehouse_receive: {
    received: "Received",
    transferred: "Transferred",
    temperature_breach: "Temperature breach",
    queued: "Queued",
  },
};

function tone(label: string) {
  const l = label.toLowerCase();
  if (l.includes("authentic") || l.includes("passed") || l.includes("verified") || l === "received")
    return "border-emerald-500/50 bg-emerald-500/10 text-emerald-100";
  if (l.includes("queued")) return "border-slate-500/50 bg-slate-800/50 text-slate-200";
  if (l.includes("breach") || l.includes("seized") || l.includes("recall"))
    return "border-rose-500/50 bg-rose-500/15 text-rose-100";
  return "border-amber-500/50 bg-amber-500/10 text-amber-100";
}

export function ScanResultCard({
  result,
  scanType,
}: {
  result: ScanIngestResult;
  scanType: ScanType;
}) {
  const label =
    OUTCOME_LABELS[scanType][result.outcome_label] ?? result.outcome_label.replace(/_/g, " ");

  return (
    <div className={`rounded-xl border px-4 py-3 ${tone(result.outcome_label)}`}>
      <p className="text-lg font-semibold capitalize">{label}</p>
      <p className="mt-1 font-mono text-xs opacity-80">{result.serial_number}</p>
      <p className="mt-2 text-xs opacity-70">
        Risk {result.risk_score.toFixed(0)} · Sync {result.sync_status}
      </p>
    </div>
  );
}
