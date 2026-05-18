"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { ScanIngestPayload } from "@/services/scanning";

export type QueuedScan = ScanIngestPayload & {
  id: string;
  queued_at: string;
  attempts: number;
  last_error?: string;
  client_sync_status: "pending" | "syncing" | "synced" | "failed";
};

type OfflineScanQueueState = {
  deviceId: string;
  queue: QueuedScan[];
  enqueue: (item: Omit<QueuedScan, "id" | "queued_at" | "attempts" | "client_sync_status">) => void;
  markSyncing: (id: string) => void;
  markSynced: (id: string) => void;
  markFailed: (id: string, error: string) => void;
  remove: (id: string) => void;
  ensureDeviceId: () => string;
};

function newId() {
  return `q-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

export const useOfflineScanQueue = create<OfflineScanQueueState>()(
  persist(
    (set, get) => ({
      deviceId: "",
      queue: [],
      ensureDeviceId: () => {
        const existing = get().deviceId;
        if (existing) return existing;
        const id = `nptte-${typeof crypto !== "undefined" && crypto.randomUUID ? crypto.randomUUID() : newId()}`;
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
      markSynced: (id) =>
        set((s) => ({
          queue: s.queue.filter((r) => r.id !== id),
        })),
      remove: (id) => set((s) => ({ queue: s.queue.filter((r) => r.id !== id) })),
    }),
    { name: "nptte-offline-scan-queue" }
  )
);
