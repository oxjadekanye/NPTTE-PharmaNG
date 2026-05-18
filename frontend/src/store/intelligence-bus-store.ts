import { create } from "zustand";
import type { DemoFeedEvent, DemoSeverity } from "@/demo/types";

export type IntelligenceChannel =
  | "scan"
  | "supply_chain"
  | "dispense"
  | "customs"
  | "recall"
  | "shortage"
  | "investigation";

export interface BusEvent extends DemoFeedEvent {
  channel: IntelligenceChannel;
  stateCode?: string;
}

interface IntelligenceBusState {
  nationalThreatIndex: number;
  bus: BusEvent[];
  lastEscalationAt: string | null;
  push: (e: Omit<BusEvent, "id" | "at"> & { id?: string }) => void;
  tickNationalIndex: () => void;
  escalate: (message: string, severity: DemoSeverity) => void;
}

const CHANNELS: IntelligenceChannel[] = [
  "scan",
  "supply_chain",
  "dispense",
  "customs",
  "recall",
  "shortage",
  "investigation",
];

export const useIntelligenceBusStore = create<IntelligenceBusState>((set, get) => ({
  nationalThreatIndex: 58,
  bus: [],
  lastEscalationAt: null,
  push: (e) => {
    const event: BusEvent = {
      ...e,
      id: e.id ?? `bus-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
      at: new Date().toISOString(),
    };
    set((s) => ({ bus: [event, ...s.bus].slice(0, 200) }));
    const sev = e.severity;
    if (sev === "critical" || sev === "high") {
      get().tickNationalIndex();
    }
  },
  tickNationalIndex: () =>
    set((s) => {
      const delta = (Math.random() - 0.45) * 4;
      const next = Math.min(96, Math.max(12, Math.round((s.nationalThreatIndex + delta) * 10) / 10));
      return { nationalThreatIndex: next };
    }),
  escalate: (message, severity) => {
    get().push({
      type: "escalation",
      channel: "investigation",
      message,
      severity,
    });
    set({ lastEscalationAt: new Date().toISOString() });
  },
}));

export function randomSimulatedBusEvent(): Omit<BusEvent, "id" | "at"> {
  const channel = CHANNELS[Math.floor(Math.random() * CHANNELS.length)];
  const messages: Record<IntelligenceChannel, string[]> = {
    scan: [
      "Citizen verification burst — FCT (+18% vs baseline)",
      "Duplicate serial cluster — Rivers state corridor",
    ],
    supply_chain: [
      "Cold-chain telemetry deviation — Lagos → Abuja lane",
      "Warehouse handoff SLA breach — Ibadan hub",
    ],
    dispense: [
      "Pharmacy dispense without prior custody scan — flagged",
      "High-value ARV dispense chain verified — Enugu",
    ],
    customs: [
      "Manifest AP-882 risk score 76 — secondary inspection queued",
      "Border post Jibia: watchlist ingredient match",
    ],
    recall: [
      "Recall REC-NG-2026-018 propagation 62% pharmacy ACK",
      "Destruction confirmation pending — Ogun facilities",
    ],
    shortage: [
      "Insulin national watchlist — Enugu below 72h cover",
      "Paediatric amoxicillin demand shock — Kano",
    ],
    investigation: [
      "Inter-agency task force sync — INC-2026-0142",
      "Evidence chain sealed — NDLEA liaison",
    ],
  };
  const pool = messages[channel];
  const message = pool[Math.floor(Math.random() * pool.length)] ?? "National intelligence pulse";
  const severities: DemoSeverity[] = ["low", "medium", "high", "critical"];
  const severity = severities[Math.floor(Math.random() * severities.length)];
  return { channel, type: channel, message, severity };
}
