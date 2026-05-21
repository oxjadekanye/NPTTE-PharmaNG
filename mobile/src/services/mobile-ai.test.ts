import { describe, expect, it } from "vitest";
import {
  checklistFallbackRecommendation,
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
