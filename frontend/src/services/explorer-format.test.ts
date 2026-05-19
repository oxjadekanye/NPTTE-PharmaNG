import { describe, it, expect } from "vitest";
import { normalizeExplorerRecords, formatLocation } from "./explorer-format";

describe("normalizeExplorerRecords", () => {
  it("unwraps paginated items", () => {
    const rows = normalizeExplorerRecords({
      items: [{ id: "1", title: "Alert A" }],
      page: 1,
      total: 1,
    });
    expect(rows).toHaveLength(1);
    expect(rows[0].title).toBe("Alert A");
  });

  it("returns empty for invalid input", () => {
    expect(normalizeExplorerRecords(null)).toEqual([]);
  });
});

describe("formatLocation", () => {
  it("includes organisation and full address", () => {
    const line = formatLocation({
      organisation: "Lagos Central Pharmacy",
      organisation_type: "pharmacy",
      address: "12 Broad Street",
      city: "Lagos",
      state: "Lagos",
    });
    expect(line).toContain("Lagos Central Pharmacy");
    expect(line).toContain("Broad Street");
  });
});
