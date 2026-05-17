/**
 * Server-Sent Events abstraction — reconnects with backoff for live dashboards.
 */

export type RealtimeMessage = {
  type: string;
  payload: unknown;
  timestamp?: string;
};

type Listener = (msg: RealtimeMessage) => void;

export class SseClient {
  private source: EventSource | null = null;
  private listeners = new Set<Listener>();
  private reconnectMs = 1000;
  private maxReconnectMs = 30000;

  constructor(private url: string) {}

  connect(token?: string) {
    this.disconnect();
    const url = new URL(this.url);
    if (token) url.searchParams.set("token", token);
    this.source = new EventSource(url.toString(), { withCredentials: false });

    this.source.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data) as RealtimeMessage;
        this.listeners.forEach((fn) => fn(data));
      } catch {
        /* ignore malformed */
      }
    };

    this.source.onerror = () => {
      this.disconnect();
      setTimeout(() => {
        this.reconnectMs = Math.min(this.reconnectMs * 2, this.maxReconnectMs);
        this.connect(token);
      }, this.reconnectMs);
    };

    this.source.onopen = () => {
      this.reconnectMs = 1000;
    };
  }

  subscribe(fn: Listener) {
    this.listeners.add(fn);
    return () => this.listeners.delete(fn);
  }

  disconnect() {
    this.source?.close();
    this.source = null;
  }
}

export function createRealtimeClient(): SseClient {
  const base =
    process.env.NEXT_PUBLIC_REALTIME_SSE_URL ??
    `${process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1"}/realtime/stream/`;
  return new SseClient(base);
}
