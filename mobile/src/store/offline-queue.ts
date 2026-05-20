import AsyncStorage from "@react-native-async-storage/async-storage";
import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";
import type { ScanIngestPayload } from "@/services/scanning";

export type QueuedScan = ScanIngestPayload & {
  id: string;
  queued_at: string;
  attempts: number;
  priority: number;
  last_error?: string;
  client_sync_status: "pending" | "syncing" | "synced" | "failed";
};

type OfflineQueueState = {
  deviceId: string;
  lastSyncAt: string | null;
  queue: QueuedScan[];
  enqueue: (
    item: Omit<QueuedScan, "id" | "queued_at" | "attempts" | "client_sync_status" | "priority">
  ) => void;
  markSyncing: (id: string) => void;
  markSynced: (id: string) => void;
  markFailed: (id: string, error: string) => void;
  remove: (id: string) => void;
  ensureDeviceId: () => string;
  setLastSyncAt: (iso: string) => void;
  nextBackoffMs: (attempts: number) => number;
};

function newId() {
  return `m-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

export const useOfflineQueue = create<OfflineQueueState>()(
  persist(
    (set, get) => ({
      deviceId: "",
      lastSyncAt: null,
      queue: [],
      setLastSyncAt: (iso) => set({ lastSyncAt: iso }),
      nextBackoffMs: (attempts) => Math.min(60000, 2000 * 2 ** attempts),
      ensureDeviceId: () => {
        const existing = get().deviceId;
        if (existing) return existing;
        const id = `nptte-mobile-${newId()}`;
        set({ deviceId: id });
        return id;
      },
      enqueue: (item) =>
        set((s) => {
          const entry: QueuedScan = {
            ...item,
            id: newId(),
            queued_at: new Date().toISOString(),
            attempts: 0,
            priority: item.scan_type === "regulator_inspection" ? 10 : 5,
            client_sync_status: "pending",
            sync_status: "pending",
            device_id: item.device_id || s.deviceId || get().ensureDeviceId(),
          };
          return { queue: [entry, ...s.queue].slice(0, 200) };
        }),
      markSyncing: (id) =>
        set((s) => ({
          queue: s.queue.map((r) =>
            r.id === id ? { ...r, client_sync_status: "syncing" as const } : r
          ),
        })),
      markFailed: (id, error) =>
        set((s) => ({
          queue: s.queue.map((r) =>
            r.id === id
              ? {
                  ...r,
                  client_sync_status: "failed" as const,
                  attempts: r.attempts + 1,
                  last_error: error,
                }
              : r
          ),
        })),
      markSynced: (id) => set((s) => ({ queue: s.queue.filter((r) => r.id !== id) })),
      remove: (id) => set((s) => ({ queue: s.queue.filter((r) => r.id !== id) })),
    }),
    {
      name: "nptte-mobile-offline-queue",
      storage: createJSONStorage(() => AsyncStorage),
      onRehydrateStorage: () => (state) => {
        if (!state?.queue) return;
        const valid = state.queue.filter(
          (r) => r && typeof r.id === "string" && typeof r.serial_number === "string"
        );
        if (valid.length !== state.queue.length) {
          useOfflineQueue.setState({ queue: valid });
        }
      },
    }
  )
);

/** Repair corrupted queue entries after bad persist. */
export function validateOfflineQueue() {
  const q = useOfflineQueue.getState().queue;
  const valid = q.filter((r) => r?.id && r.serial_number);
  if (valid.length !== q.length) useOfflineQueue.setState({ queue: valid });
  return valid.length;
}
