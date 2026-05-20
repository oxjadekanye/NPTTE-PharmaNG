import { useCallback, useEffect } from "react";
import { syncEvidenceQueue, uploadFieldEvidence } from "@/services/evidence";
import { useEvidenceQueue } from "@/store/evidence-queue";
import { useOfflineQueue } from "@/store/offline-queue";
import { useNetwork } from "@/hooks/useNetwork";

export function useEvidenceSync() {
  const { online } = useNetwork();
  const queue = useEvidenceQueue((s) => s.queue);
  const markSynced = useEvidenceQueue((s) => s.markSynced);
  const markFailed = useEvidenceQueue((s) => s.markFailed);
  const markSyncing = useEvidenceQueue((s) => s.markSyncing);
  const nextBackoffMs = useEvidenceQueue((s) => s.nextBackoffMs);
  const setLastSync = useEvidenceQueue((s) => s.setLastSync);
  const ensureDeviceId = useOfflineQueue((s) => s.ensureDeviceId);

  const syncPending = useCallback(async () => {
    if (!online) return;
    const now = Date.now();
    const pending = queue.filter((q) => {
      if (q.client_sync_status !== "pending" && q.client_sync_status !== "failed") return false;
      const backoff = nextBackoffMs(q.attempts);
      const queuedMs = new Date(q.queued_at).getTime();
      return now - queuedMs >= backoff;
    });
    for (const item of pending) {
      markSyncing(item.id);
      const res = await uploadFieldEvidence({
        device_id: ensureDeviceId(),
        evidence_type: item.evidence_type,
        notes: item.notes,
        serial_number: item.serial_number,
        photos: item.photos,
      });
      if (res.success) markSynced(item.id);
      else markFailed(item.id, res.message);
    }
    if (pending.length > 0) {
      void syncEvidenceQueue(ensureDeviceId());
      setLastSync(new Date().toISOString());
    }
  }, [online, queue, markSynced, markFailed, markSyncing, nextBackoffMs, setLastSync, ensureDeviceId]);

  useEffect(() => {
    const id = setTimeout(() => void syncPending(), 500);
    return () => clearTimeout(id);
  }, [syncPending]);

  return { syncPending };
}
