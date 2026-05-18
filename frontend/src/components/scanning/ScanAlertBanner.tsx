"use client";

import type { ScanIngestResult } from "@/services/scanning";

const ALERT_STYLES = {
  recall: "border-rose-500/60 bg-rose-500/15 text-rose-100",
  suspicious: "border-amber-500/60 bg-amber-500/15 text-amber-100",
  counterfeit: "border-red-500/60 bg-red-500/15 text-red-100",
  sync: "border-violet-500/60 bg-violet-500/15 text-violet-100",
};

export function ScanAlertBanner({ result }: { result?: ScanIngestResult | null }) {
  if (!result?.alerts) return null;
  const { recall_alert, suspicious_scan_alert, counterfeit_warning, failed_sync_warning } =
    result.alerts;

  return (
    <div className="space-y-2">
      {recall_alert && (
        <p className={`rounded-lg border px-3 py-2 text-sm ${ALERT_STYLES.recall}`}>
          Recall alert — check national recall register before dispensing.
        </p>
      )}
      {suspicious_scan_alert && (
        <p className={`rounded-lg border px-3 py-2 text-sm ${ALERT_STYLES.suspicious}`}>
          Suspicious scan — escalate to regulator workflow.
        </p>
      )}
      {counterfeit_warning && (
        <p className={`rounded-lg border px-3 py-2 text-sm ${ALERT_STYLES.counterfeit}`}>
          Counterfeit risk elevated — quarantine and report.
        </p>
      )}
      {failed_sync_warning && (
        <p className={`rounded-lg border px-3 py-2 text-sm ${ALERT_STYLES.sync}`}>
          Sync failed — scan retained in offline queue for retry.
        </p>
      )}
    </div>
  );
}
