import { create } from "zustand";

export type RealtimePatch = {
  scope: "metric" | "entity" | "context" | "investigation" | "channel" | "drawer";
  target: string;
  ops: Record<string, unknown>;
};

type PatchState = {
  patches: RealtimePatch[];
  metrics: Record<string, Record<string, unknown>>;
  applyPatch: (patch: RealtimePatch) => void;
  clear: () => void;
};

export const useRealtimePatchStore = create<PatchState>((set, get) => ({
  patches: [],
  metrics: {},
  applyPatch: (patch) => {
    set((s) => {
      const key = `${patch.scope}:${patch.target}`;
      const dup = s.patches[0] && `${s.patches[0].scope}:${s.patches[0].target}` === key;
      const patches = dup ? s.patches : [patch, ...s.patches].slice(0, 200);
      let metrics = s.metrics;
      if (patch.scope === "metric") {
        metrics = {
          ...metrics,
          [patch.target]: { ...(metrics[patch.target] ?? {}), ...patch.ops },
        };
      }
      return { patches, metrics };
    });
  },
  clear: () => set({ patches: [], metrics: {} }),
}));

export function selectMetric(target: string) {
  return (s: PatchState) => s.metrics[target];
}
