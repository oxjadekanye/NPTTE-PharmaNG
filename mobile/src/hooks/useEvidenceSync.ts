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
  const setLastSync = useEvidenceQueue((s) => s.setLastSync);
  const ensureDeviceId = useOfflineQueue((s) => s.ensureDeviceId);

  const syncPending = useCallback(async () => {
    if (!online) return;
    const pending = queue.filter((q) => q.client_sync_status === "pending");
    for (const item of pending) {
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
  }, [online, queue, markSynced, markFailed, setLastSync, ensureDeviceId]);

  useEffect(() => {
    void syncPending();
  }, [syncPending]);

  return { syncPending };
}
