import { describe, expect, it } from "vitest";
import {
  getAverageApiLatency,
  getRecentMetrics,
  recordApiLatency,
  recordMetric,
} from "@/services/performance-monitor";

describe("performance-monitor", () => {
  it("records API latency and computes average", () => {
    recordApiLatency("/mobile/health/", 120, true);
    recordApiLatency("/mobile/health/", 80, true);
    expect(getAverageApiLatency()).toBe(100);
  });

  it("stores recent metrics", () => {
    recordMetric("scan", "test-scan", 45);
    const recent = getRecentMetrics(5);
    expect(recent.some((m) => m.label === "test-scan")).toBe(true);
  });
});
