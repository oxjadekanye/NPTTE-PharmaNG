"use client";

import { useEffect } from "react";
import { useRealtimePatchStore, type RealtimePatch } from "@/store/realtime-patch-store";

export function useRealtimePatches(enabled = true, channel?: string) {
  const applyPatch = useRealtimePatchStore((s) => s.applyPatch);
  const patches = useRealtimePatchStore((s) => s.patches);
  const metrics = useRealtimePatchStore((s) => s.metrics);

  useEffect(() => {
    if (!enabled || typeof window === "undefined") return;
    const base =
      process.env.NEXT_PUBLIC_REALTIME_SSE_URL ??
      `${process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1"}/realtime/stream/`;
    const url = new URL(base);
    url.searchParams.set("patches", "1");
    if (channel) url.searchParams.set("channel", channel);
    const token = localStorage.getItem("nptte_access_token");
    if (token) url.searchParams.set("token", token);

    const es = new EventSource(url.toString());

    es.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data) as { type: string; payload: unknown };
        if (data.type === "patch" && data.payload && typeof data.payload === "object") {
          applyPatch(data.payload as RealtimePatch);
        }
      } catch {
        /* ignore */
      }
    };

    return () => es.close();
  }, [enabled, channel, applyPatch]);

  return { patches, metrics };
}
