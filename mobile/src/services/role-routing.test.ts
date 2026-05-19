import { describe, expect, it } from "vitest";
import { mobileHomePath, resolveMobileRole } from "@/services/role-routing";

describe("resolveMobileRole", () => {
  it("maps pharmacy roles", () => {
    expect(resolveMobileRole("PHARMACY_STAFF")).toBe("pharmacy");
  });

  it("maps customs admin", () => {
    expect(resolveMobileRole("CUSTOMS_ADMIN")).toBe("customs");
  });

  it("maps warehouse manager", () => {
    expect(resolveMobileRole("WAREHOUSE_MANAGER")).toBe("warehouse");
  });

  it("maps executive FMOH", () => {
    expect(resolveMobileRole("FMOH_ADMIN")).toBe("executive");
  });

  it("maps regulator when flag set", () => {
    expect(resolveMobileRole("STATE_REGULATOR", true)).toBe("regulator");
  });

  it("maps patient to citizen mobile home", () => {
    expect(resolveMobileRole("PATIENT")).toBe("citizen");
  });
});

describe("mobileHomePath", () => {
  it("returns regulator home", () => {
    expect(mobileHomePath("regulator")).toBe("/regulator");
  });
});
