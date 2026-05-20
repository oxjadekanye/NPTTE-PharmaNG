import { create } from "zustand";

export type ToastKind = "info" | "success" | "warning" | "error";

export type ToastMessage = {
  id: string;
  kind: ToastKind;
  text: string;
  at: number;
};

type ToastState = {
  current: ToastMessage | null;
  show: (text: string, kind?: ToastKind) => void;
  dismiss: () => void;
};

export const useOperationalToast = create<ToastState>((set, get) => ({
  current: null,
  show: (text, kind = "info") => {
    const id = `toast-${Date.now()}`;
    set({ current: { id, kind, text, at: Date.now() } });
    setTimeout(() => {
      if (get().current?.id === id) set({ current: null });
    }, 4000);
  },
  dismiss: () => set({ current: null }),
}));
