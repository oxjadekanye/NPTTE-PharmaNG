import { describe, expect, it } from "vitest";
import {
  computeInspectionScore,
  failedInspectionItems,
  inspectionItemKey,
  sectionPassed,
} from "@/services/mobile-inspection";

describe("mobile-inspection", () => {
  it("computes score from checked items", () => {
    const checks: Record<string, boolean> = {};
    checks[inspectionItemKey("site", "Registration displayed")] = true;
    expect(computeInspectionScore(checks)).toBeGreaterThan(0);
  });

  it("detects failed product items", () => {
    const failed = failedInspectionItems({});
    expect(failed.some((f) => f.includes("Product"))).toBe(true);
    expect(sectionPassed("product", {})).toBe(false);
  });
});
