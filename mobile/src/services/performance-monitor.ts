/**
 * Phase 24 — lightweight performance instrumentation (no external deps).
 */
type MetricKind = "startup" | "route" | "scan" | "api" | "render" | "memory";

export type PerformanceMetric = {
  kind: MetricKind;
  label: string;
  durationMs: number;
  at: string;
  meta?: Record<string, unknown>;
};

const metrics: PerformanceMetric[] = [];
const marks = new Map<string, number>();
let startupMs: number | null = null;

export function markAppStart() {
  marks.set("app.start", Date.now());
}

export function markAppReady() {
  const start = marks.get("app.start");
  if (!start) return;
  startupMs = Date.now() - start;
  recordMetric("startup", "cold_boot", startupMs);
}

export function startTimer(label: string) {
  marks.set(label, Date.now());
}

export function endTimer(kind: MetricKind, label: string, meta?: Record<string, unknown>) {
  const start = marks.get(label);
  if (start == null) return;
  marks.delete(label);
  recordMetric(kind, label, Date.now() - start, meta);
}

export function recordMetric(
  kind: MetricKind,
  label: string,
  durationMs: number,
  meta?: Record<string, unknown>
) {
  metrics.unshift({
    kind,
    label,
    durationMs: Math.round(durationMs),
    at: new Date().toISOString(),
    meta,
  });
  if (metrics.length > 80) metrics.pop();
}

export function recordApiLatency(path: string, durationMs: number, ok: boolean) {
  recordMetric("api", path, durationMs, { ok });
}

/** Placeholder — wire native memory sampler in production hardening. */
export function sampleMemoryPlaceholder(): { heapUsedMb: number | null; note: string } {
  return {
    heapUsedMb: null,
    note: "Native memory sampling not wired — placeholder for Phase 24+",
  };
}

export function getStartupMs() {
  return startupMs;
}

export function getRecentMetrics(limit = 25) {
  return metrics.slice(0, limit);
}

export function getAverageApiLatency() {
  const api = metrics.filter((m) => m.kind === "api");
  if (api.length === 0) return null;
  return Math.round(api.reduce((n, m) => n + m.durationMs, 0) / api.length);
}
