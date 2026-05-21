"use client";

import { useEffect, useState } from "react";
import {
  subscribeOperational,
  type OperationalEventKind,
} from "@/services/realtime/event-bus";
import { useRealtimeFeed } from "@/hooks/useRealtimeFeed";

/** Subscribe to operational kinds with shared polling feed. */
export function useOperationalSubscription(kinds: OperationalEventKind[] = ["scan"]) {
  const channels = kinds.join(",");
  const { feed, loading, refresh, invalidate } = useRealtimeFeed({ channels });
  const [events, setEvents] = useState<unknown[]>([]);

  useEffect(() => {
    const unsubs = kinds.map((kind) =>
      subscribeOperational(kind, (payload) => {
        setEvents((prev) => [payload, ...prev].slice(0, 50));
      })
    );
    return () => unsubs.forEach((u) => u());
  }, [kinds.join(",")]);

  useEffect(() => {
    if (feed?.events?.length) {
      setEvents(feed.events.filter((e) => kinds.includes(String(e.kind) as OperationalEventKind)));
    }
  }, [feed, kinds.join(",")]);

  return { events, feed, loading, refresh, invalidate };
}
