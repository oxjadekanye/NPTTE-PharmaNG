import AsyncStorage from "@react-native-async-storage/async-storage";
import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";
import type { EvidencePhoto } from "@/services/evidence";

export type QueuedEvidence = {
  id: string;
  evidence_type: string;
  notes: string;
  serial_number: string;
  photos: EvidencePhoto[];
  queued_at: string;
  attempts: number;
  client_sync_status: "pending" | "syncing" | "synced" | "failed";
  last_error?: string;
};

type EvidenceQueueState = {
  queue: QueuedEvidence[];
  lastSyncAt: string | null;
  enqueue: (item: Omit<QueuedEvidence, "id" | "queued_at" | "attempts" | "client_sync_status">) => void;
  markSyncing: (id: string) => void;
  markSynced: (id: string) => void;
  markFailed: (id: string, error: string) => void;
  setLastSync: (iso: string) => void;
  nextBackoffMs: (attempts: number) => number;
};

function newId() {
  return `ev-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`;
}

export const useEvidenceQueue = create<EvidenceQueueState>()(
  persist(
    (set) => ({
      queue: [],
      lastSyncAt: null,
      nextBackoffMs: (attempts) => Math.min(120_000, 3000 * 2 ** attempts),
      markSyncing: (id) =>
        set((s) => ({
          queue: s.queue.map((q) =>
            q.id === id ? { ...q, client_sync_status: "syncing" as const } : q
          ),
        })),
      enqueue: (item) =>
        set((s) => ({
          queue: [
            {
              ...item,
              id: newId(),
              queued_at: new Date().toISOString(),
              attempts: 0,
              client_sync_status: "pending" as const,
            },
            ...s.queue,
          ].slice(0, 50),
        })),
      markSynced: (id) => set((s) => ({ queue: s.queue.filter((q) => q.id !== id) })),
      markFailed: (id, error) =>
        set((s) => ({
          queue: s.queue.map((q) =>
            q.id === id
              ? { ...q, client_sync_status: "failed" as const, attempts: q.attempts + 1, last_error: error }
              : q
          ),
        })),
      setLastSync: (iso) => set({ lastSyncAt: iso }),
    }),
    { name: "nptte-evidence-queue", storage: createJSONStorage(() => AsyncStorage) }
  )
);
