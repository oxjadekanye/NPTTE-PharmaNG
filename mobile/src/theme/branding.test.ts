import { describe, expect, it } from "vitest";
import { NPTTEBrand } from "@/theme/branding";

describe("NPTTEBrand", () => {
  it("exports sovereign palette", () => {
    expect(NPTTEBrand.colors.sovereign.bg).toBe("#020617");
    expect(NPTTEBrand.colors.alert.danger).toBeDefined();
    expect(NPTTEBrand.spacing.lg).toBe(16);
  });

  it("defines operational gradients", () => {
    expect(NPTTEBrand.gradients.operational.length).toBe(2);
  });
});
