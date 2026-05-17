"use client";

import { useEffect, useState } from "react";
import { createRealtimeClient, type RealtimeMessage } from "@/realtime/sse-client";

export function useRealtime(enabled = true) {
  const [messages, setMessages] = useState<RealtimeMessage[]>([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    if (!enabled || typeof window === "undefined") return;
    const client = createRealtimeClient();
    const token = localStorage.getItem("nptte_access_token") ?? undefined;
    client.connect(token);
    setConnected(true);
    const unsub = client.subscribe((msg) => {
      setMessages((prev) => [msg, ...prev].slice(0, 100));
    });
    return () => {
      unsub();
      client.disconnect();
      setConnected(false);
    };
  }, [enabled]);

  return { messages, connected };
}
