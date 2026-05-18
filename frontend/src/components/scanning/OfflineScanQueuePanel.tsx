"use client";

import { useState } from "react";
import { useOfflineScanQueue } from "@/store/offline-scan-queue-store";
import { syncOfflineScans, type ScanIngestPayload } from "@/services/scanning";

export function OfflineScanQueuePanel() {
  const queue = useOfflineScanQueue((s) => s.queue);
  const markSyncing = useOfflineScanQueue((s) => s.markSyncing);
  const markSynced = useOfflineScanQueue((s) => s.markSynced);
  const markFailed = useOfflineScanQueue((s) => s.markFailed);
  const [syncing, setSyncing] = useState(false);

  if (!queue.length) return null;

  async function retryAll() {
    setSyncing(true);
    const pending = queue.filter((q) => q.client_sync_status !== "synced");
    for (const item of pending) {
      markSyncing(item.id);
    }
    try {
      const payload: ScanIngestPayload[] = pending.map((q) => ({
        serial_number: q.serial_number,
        scan_type: q.scan_type,
        actor_role: q.actor_role,
        device_id: q.device_id,
        latitude: q.latitude,
        longitude: q.longitude,
        offline_timestamp: q.offline_timestamp ?? q.queued_at,
        replay_nonce: q.replay_nonce,
      }));
      await syncOfflineScans(payload);
      pending.forEach((q) => markSynced(q.id));
    } catch (e) {
      pending.forEach((q) =>
        markFailed(q.id, e instanceof Error ? e.message : "Sync failed")
      );
    } finally {
      setSyncing(false);
    }
  }

  return (
    <div className="rounded-xl border border-violet-500/40 bg-violet-500/10 p-4">
      <div className="flex items-center justify-between gap-2">
        <h3 className="text-sm font-semibold text-violet-100">
          Offline queue ({queue.length})
        </h3>
        <button
          type="button"
          onClick={retryAll}
          disabled={syncing}
          className="rounded-lg bg-violet-600 px-3 py-1.5 text-xs font-medium text-white disabled:opacity-50"
        >
          {syncing ? "Syncing…" : "Retry sync"}
        </button>
      </div>
      <ul className="mt-3 max-h-40 space-y-2 overflow-y-auto text-xs">
        {queue.map((q) => (
          <li
            key={q.id}
            className="flex justify-between gap-2 rounded border border-sovereign-800/80 bg-sovereign-950/50 px-2 py-1.5"
          >
            <span className="truncate font-mono text-slate-300">{q.serial_number}</span>
            <span className="shrink-0 text-slate-500">
              {q.client_sync_status} · {q.attempts} tries
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
