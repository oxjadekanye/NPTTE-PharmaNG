import { useCallback, useEffect, useState } from "react";
import {
  fetchOperationalFeedMobile,
  type MobileOperationalFeed,
} from "@/services/realtime/operational-feed";
import { useNetwork } from "@/hooks/useNetwork";

const INTERVAL_MS = 20000;

export function useRealtimeFeed(channels?: string) {
  const { online } = useNetwork();
  const [feed, setFeed] = useState<MobileOperationalFeed | null>(null);
  const [loading, setLoading] = useState(false);

  const refresh = useCallback(async () => {
    if (!online) return;
    setLoading(true);
    try {
      const res = await fetchOperationalFeedMobile(channels);
      if (res.success && res.data) setFeed(res.data);
    } finally {
      setLoading(false);
    }
  }, [online, channels]);

  useEffect(() => {
    void refresh();
    if (!online) return;
    const id = setInterval(() => void refresh(), INTERVAL_MS);
    return () => clearInterval(id);
  }, [refresh, online]);

  return { feed, loading, refresh, online };
}
