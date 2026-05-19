import { create } from "zustand";

export type ExplorerOpenPayload = {
  entityType: string;
  entityId: string;
  title?: string;
  contextKey?: string;
  cachedSummary?: Record<string, unknown>;
};

type ExplorerDrawerState = {
  open: boolean;
  target: ExplorerOpenPayload | null;
  openDrawer: (target: ExplorerOpenPayload) => void;
  closeDrawer: () => void;
};

export const useExplorerDrawerStore = create<ExplorerDrawerState>((set) => ({
  open: false,
  target: null,
  openDrawer: (target) => set({ open: true, target }),
  closeDrawer: () => set({ open: false, target: null }),
}));
