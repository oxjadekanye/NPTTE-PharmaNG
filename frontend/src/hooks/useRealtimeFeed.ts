"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  fetchOperationalFeed,
  invalidateOperationalFeed,
  type OperationalFeedPayload,
} from "@/services/realtime/polling";

const DEFAULT_INTERVAL_MS = 15000;

export function useRealtimeFeed(options?: {
  channels?: string;
  enabled?: boolean;
  intervalMs?: number;
}) {
  const enabled = options?.enabled ?? true;
  const [feed, setFeed] = useState<OperationalFeedPayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const sinceRef = useRef(0);

  const refresh = useCallback(
    async (force = false) => {
      if (!enabled) return;
      setLoading(true);
      setError(null);
      try {
        const res = await fetchOperationalFeed({
          since_sequence: sinceRef.current,
          channels: options?.channels,
          force,
        });
        if (res.success && res.data) {
          setFeed(res.data);
          sinceRef.current = res.data.since_sequence ?? sinceRef.current;
        } else {
          setError(res.message || "Feed unavailable");
        }
      } catch (e) {
        setError(e instanceof Error ? e.message : "Feed error");
      } finally {
        setLoading(false);
      }
    },
    [enabled, options?.channels]
  );

  useEffect(() => {
    void refresh();
    if (!enabled) return;
    const id = setInterval(() => void refresh(), options?.intervalMs ?? DEFAULT_INTERVAL_MS);
    return () => clearInterval(id);
  }, [refresh, enabled, options?.intervalMs]);

  const invalidate = useCallback(() => {
    invalidateOperationalFeed();
    void refresh(true);
  }, [refresh]);

  return { feed, loading, error, refresh, invalidate, connected: enabled && !error };
}
