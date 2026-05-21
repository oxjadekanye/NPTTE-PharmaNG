import { useCallback } from "react";
import { runOfflineScanSync, type SyncRunResult } from "@/services/offline-scan-sync";
import { useOfflineQueue } from "@/store/offline-queue";
import { useNetwork } from "@/hooks/useNetwork";

export type { SyncRunResult };

export function useOfflineSync() {
  const { online } = useNetwork();
  const queue = useOfflineQueue((s) => s.queue);
  const lastSyncAt = useOfflineQueue((s) => s.lastSyncAt);

  const syncAll = useCallback(async (): Promise<SyncRunResult> => {
    return runOfflineScanSync(online);
  }, [online]);

  const pendingCount = queue.filter(
    (q) => q.client_sync_status === "pending" || q.client_sync_status === "failed"
  ).length;

  return {
    online,
    pendingCount,
    failedCount: queue.filter((q) => q.client_sync_status === "failed").length,
    syncAll,
    queue,
    lastSyncAt,
  };
}
