import { syncOfflineScans } from "@/services/scanning";
import { useOfflineQueue } from "@/store/offline-queue";

export type SyncRunResult = {
  synced: number;
  failed: number;
  attempted: number;
  error?: "offline" | "empty";
  message: string;
  attemptedAt: string;
};

/** Runs scan queue sync using fresh store state (safe for button handlers). */
export async function runOfflineScanSync(online: boolean): Promise<SyncRunResult> {
  const attemptedAt = new Date().toISOString();
  if (!online) {
    return {
      synced: 0,
      failed: 0,
      attempted: 0,
      error: "offline",
      message: "You are offline. Connect to the network to sync scans.",
      attemptedAt,
    };
  }

  const store = useOfflineQueue.getState();
  const pending = [...store.queue]
    .filter((q) => q.client_sync_status === "pending" || q.client_sync_status === "failed")
    .sort((a, b) => b.priority - a.priority);

  if (pending.length === 0) {
    return {
      synced: 0,
      failed: 0,
      attempted: 0,
      error: "empty",
      message: "No pending scans to sync",
      attemptedAt,
    };
  }

  let synced = 0;
  let failed = 0;

  for (const item of pending) {
    if (item.attempts > 0) {
      await new Promise((r) => setTimeout(r, store.nextBackoffMs(item.attempts)));
    }
    store.markSyncing(item.id);
    const { id, queued_at, attempts, client_sync_status, last_error, priority, ...payload } = item;
    try {
      const res = await syncOfflineScans([payload]);
      if (!res.success) {
        store.markFailed(item.id, res.message || "Sync failed");
        failed += 1;
        continue;
      }
      store.markSynced(item.id);
      synced += 1;
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Sync request failed";
      store.markFailed(item.id, msg);
      failed += 1;
    }
  }

  useOfflineQueue.getState().setLastSyncAt(attemptedAt);

  const message =
    synced === 0 && failed > 0
      ? `Sync failed for ${failed} scan(s). Check errors below.`
      : `Synced ${synced} · failed ${failed}`;

  return { synced, failed, attempted: pending.length, message, attemptedAt };
}
