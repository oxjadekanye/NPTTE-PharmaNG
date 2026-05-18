import { create } from "zustand";
import { INITIAL_FEED, TICKER_MESSAGES } from "@/demo/nigeria-intelligence";
import type { DemoFeedEvent } from "@/demo/types";

export type CommandMode = "operational" | "ministerial";

interface CommandState {
  mode: CommandMode;
  feed: DemoFeedEvent[];
  ticker: string[];
  activityLog: string[];
  setMode: (mode: CommandMode) => void;
  pushFeed: (event: DemoFeedEvent) => void;
  pushActivity: (line: string) => void;
  rotateTicker: () => void;
}

export const useCommandStore = create<CommandState>((set) => ({
  mode: "operational",
  feed: INITIAL_FEED,
  ticker: TICKER_MESSAGES,
  activityLog: [
    "[08:45] Chain-of-custody sealed — INC-2026-0142",
    "[08:30] National threat map refreshed",
    "[08:15] Ministerial KPI snapshot generated (DEMO)",
  ],
  setMode: (mode) => set({ mode }),
  pushFeed: (event) =>
    set((s) => ({ feed: [event, ...s.feed].slice(0, 50) })),
  pushActivity: (line) =>
    set((s) => ({
      activityLog: [`[${new Date().toLocaleTimeString("en-NG", { hour: "2-digit", minute: "2-digit" })}] ${line}`, ...s.activityLog].slice(0, 30),
    })),
  rotateTicker: () =>
    set((s) => {
      const [first, ...rest] = s.ticker;
      return { ticker: [...rest, first] };
    }),
}));
