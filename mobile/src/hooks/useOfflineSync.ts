import { useCallback } from "react";
import { syncOfflineScans } from "@/services/scanning";
import { useOfflineQueue } from "@/store/offline-queue";
import { useNetwork } from "@/hooks/useNetwork";

export function useOfflineSync() {
  const { online } = useNetwork();
  const queue = useOfflineQueue((s) => s.queue);
  const lastSyncAt = useOfflineQueue((s) => s.lastSyncAt);
  const markSyncing = useOfflineQueue((s) => s.markSyncing);
  const markSynced = useOfflineQueue((s) => s.markSynced);
  const markFailed = useOfflineQueue((s) => s.markFailed);
  const setLastSyncAt = useOfflineQueue((s) => s.setLastSyncAt);
  const nextBackoffMs = useOfflineQueue((s) => s.nextBackoffMs);

  const syncAll = useCallback(async () => {
    if (!online) return { synced: 0, error: "offline" };
    const pending = [...queue]
      .filter((q) => q.client_sync_status === "pending" || q.client_sync_status === "failed")
      .sort((a, b) => b.priority - a.priority);
    if (pending.length === 0) return { synced: 0 };

    let synced = 0;
    for (const item of pending) {
      if (item.attempts > 0) {
        await new Promise((r) => setTimeout(r, nextBackoffMs(item.attempts)));
      }
      markSyncing(item.id);
      const { id, queued_at, attempts, client_sync_status, last_error, priority, ...payload } = item;
      const res = await syncOfflineScans([payload]);
      if (!res.success) {
        markFailed(item.id, res.message);
        continue;
      }
      markSynced(item.id);
      synced += 1;
    }
    if (synced > 0) setLastSyncAt(new Date().toISOString());
    return { synced };
  }, [online, queue, markSyncing, markSynced, markFailed, setLastSyncAt, nextBackoffMs]);

  const pendingCount = queue.filter(
    (q) => q.client_sync_status === "pending" || q.client_sync_status === "failed"
  ).length;

  return { online, pendingCount, failedCount: queue.filter((q) => q.client_sync_status === "failed").length, syncAll, queue, lastSyncAt };
}
