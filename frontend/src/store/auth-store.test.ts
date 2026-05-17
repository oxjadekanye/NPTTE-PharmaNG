import { describe, it, expect } from "vitest";
import { hasPermission } from "./auth-store";

describe("hasPermission", () => {
  it("grants admin.all", () => {
    expect(hasPermission(["admin.all"], "regulatory.read")).toBe(true);
  });

  it("checks specific permission", () => {
    expect(hasPermission(["regulatory.read"], "regulatory.read")).toBe(true);
    expect(hasPermission(["patient.profile"], "regulatory.read")).toBe(false);
  });
});
