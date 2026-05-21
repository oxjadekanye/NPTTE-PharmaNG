import { describe, expect, it } from "vitest";
import {
  checklistFallbackRecommendation,
  inspectionRecommendationFallback,
  parseCopilotText,
} from "@/services/mobile-ai-helpers";

describe("parseCopilotText", () => {
  it("combines summary and reasoning strings", () => {
    const text = parseCopilotText({
      summary: "Elevated risk",
      reasoning: "Multiple failed scans in region.",
    });
    expect(text).toContain("Elevated risk");
    expect(text).toContain("Multiple failed scans");
  });

  it("reads nested summary object", () => {
    const text = parseCopilotText({
      summary: { title: "National alert", body: "Recall active" },
      reasoning: "Act now",
    });
    expect(text).toContain("National alert");
    expect(text).toContain("Act now");
  });
});

describe("checklistFallbackRecommendation", () => {
  it("returns stricter guidance for low scores", () => {
    const low = checklistFallbackRecommendation(20);
    const high = checklistFallbackRecommendation(90);
    expect(low).toMatch(/Immediate|quarantine/i);
    expect(high).toMatch(/Maintain/i);
  });
});

describe("inspectionRecommendationFallback", () => {
  it("recommends quarantine when product checks fail", () => {
    const rec = inspectionRecommendationFallback({
      site_passed: true,
      product_passed: false,
      compliance_passed: true,
      failed_items: ["Product verification: Serial samples scanned"],
      evidence_count: 2,
      compliance_score: 55,
    });
    expect(rec.recommended_enforcement_action).toMatch(/Quarantine|serial/i);
    expect(rec.escalation_required).toBe(false);
  });

  it("flags critical score and missing evidence", () => {
    const rec = inspectionRecommendationFallback({
      site_passed: false,
      product_passed: false,
      compliance_passed: false,
      failed_items: ["Compliance: Cold-chain logs"],
      evidence_count: 0,
      compliance_score: 25,
    });
    expect(rec.risk_rating).toBe("critical");
    expect(rec.evidence_required.length).toBeGreaterThan(0);
    expect(rec.escalation_required).toBe(true);
  });
});
