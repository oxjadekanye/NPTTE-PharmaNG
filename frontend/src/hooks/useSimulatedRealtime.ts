"use client";

import { useEffect } from "react";
import { useCommandStore } from "@/store/command-store";
import type { DemoFeedEvent } from "@/demo/types";

const SIMULATED_EVENTS: Omit<DemoFeedEvent, "id" | "at">[] = [
  { type: "scan", message: "Abuja: Pharmacy verification scan — serial OK", severity: "low" },
  { type: "seizure", message: "Apapa: Customs unit flagged manifest AP-772 (DEMO)", severity: "high" },
  { type: "shortage", message: "Kano: Amoxicillin stock below regional threshold", severity: "medium" },
  { type: "fraud", message: "Lagos: Duplicate serial detected — Mushin Community Chemist", severity: "critical" },
  { type: "investigation", message: "NDLEA liaison assigned — INC-2026-0142", severity: "medium" },
  { type: "warehouse", message: "Ibadan: Scheduled warehouse inspection commenced", severity: "low" },
];

/**
 * Frontend-only simulated realtime — does not open websockets or alter backend.
 */
export function useSimulatedRealtime(enabled = true) {
  const pushFeed = useCommandStore((s) => s.pushFeed);
  const pushActivity = useCommandStore((s) => s.pushActivity);
  const rotateTicker = useCommandStore((s) => s.rotateTicker);

  useEffect(() => {
    if (!enabled) return;
    const feedInterval = setInterval(() => {
      const template = SIMULATED_EVENTS[Math.floor(Math.random() * SIMULATED_EVENTS.length)];
      const event: DemoFeedEvent = {
        ...template,
        id: `sim-${Date.now()}`,
        at: new Date().toISOString(),
      };
      pushFeed(event);
      pushActivity(event.message);
    }, 8000);
    const tickerInterval = setInterval(rotateTicker, 6000);
    return () => {
      clearInterval(feedInterval);
      clearInterval(tickerInterval);
    };
  }, [enabled, pushFeed, pushActivity, rotateTicker]);
}
