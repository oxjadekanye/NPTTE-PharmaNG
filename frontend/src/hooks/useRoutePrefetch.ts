"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { fetchPrefetchManifest } from "@/services/realtime/polling";

/** Warm Next.js routes listed in realtime prefetch manifest. */
export function useRoutePrefetch(enabled = true) {
  const router = useRouter();

  useEffect(() => {
    if (!enabled) return;
    let cancelled = false;
    void fetchPrefetchManifest().then((res) => {
      if (cancelled || !res.success || !res.data?.routes) return;
      for (const route of res.data.routes) {
        try {
          router.prefetch(route);
        } catch {
          /* ignore */
        }
      }
    });
    return () => {
      cancelled = true;
    };
  }, [enabled, router]);
}
