import { useCallback, useEffect, useRef, useState } from "react";
import { fetchMobileRealtimeFeed, type MobileFeedEvent } from "@/services/mobile-realtime";
import { useNetwork } from "@/hooks/useNetwork";
import { showLocalOperationalAlert } from "@/services/push-orchestration";

export function useMobileRealtime(channel = "officer_tasks", enabled = true) {
  const { online } = useNetwork();
  const [events, setEvents] = useState<MobileFeedEvent[]>([]);
  const sinceRef = useRef(0);

  const poll = useCallback(async () => {
    if (!online || !enabled) return;
    const res = await fetchMobileRealtimeFeed(channel, sinceRef.current);
    if (!res.success || !res.data?.events) return;
    const incoming = res.data.events;
    if (incoming.length === 0) return;
    const maxSeq = Math.max(...incoming.map((e) => e.sequence_number ?? 0), sinceRef.current);
    sinceRef.current = maxSeq;
    setEvents((prev) => {
      const merged = [...incoming, ...prev].slice(0, 40);
      return merged;
    });
    const top = incoming[0];
    const et = String(top.event_type ?? "");
    if (et.includes("recall") || et.includes("escalation") || et.includes("task")) {
      void showLocalOperationalAlert("NPTTE field alert", et);
    }
  }, [online, enabled, channel]);

  useEffect(() => {
    if (!enabled) return;
    void poll();
    const id = setInterval(() => void poll(), 20000);
    return () => clearInterval(id);
  }, [poll, enabled]);

  return { events, online, refresh: poll };
}
