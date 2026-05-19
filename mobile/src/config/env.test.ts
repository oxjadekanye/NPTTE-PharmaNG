import { describe, expect, it } from "vitest";
import { resolveAppEnvironment } from "@/config/env";

describe("resolveAppEnvironment", () => {
  it("defaults to development in vitest", () => {
    expect(resolveAppEnvironment()).toBe("development");
  });
});
