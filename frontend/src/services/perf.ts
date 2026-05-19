/** Dev-only performance marks (no-op in production builds). */
const enabled =
  typeof process !== "undefined" &&
  process.env.NODE_ENV === "development" &&
  typeof performance !== "undefined";

export function perfMark(name: string): void {
  if (!enabled) return;
  try {
    performance.mark(name);
  } catch {
    /* ignore */
  }
}

export function perfMeasure(name: string, startMark: string, endMark?: string): void {
  if (!enabled) return;
  try {
    const end = endMark ?? `${startMark}-end`;
    if (!performance.getEntriesByName(end).length) {
      performance.mark(end);
    }
    performance.measure(name, startMark, end);
    const entries = performance.getEntriesByName(name);
    const last = entries[entries.length - 1];
    if (last) {
      // eslint-disable-next-line no-console
      console.debug(`[perf] ${name}: ${last.duration.toFixed(1)}ms`);
    }
  } catch {
    /* ignore */
  }
}
