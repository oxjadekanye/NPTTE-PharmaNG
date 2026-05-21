import { describe, expect, it, vi } from "vitest";

vi.mock("@/services/api-client", () => ({ apiRequest: vi.fn() }));
vi.mock("@/services/auth-storage", () => ({}));
vi.mock("@/services/session-security", () => ({ secureLogout: vi.fn() }));

import { LOGIN_VALIDATION_HINT, parseLoginError } from "@/services/auth";

describe("parseLoginError", () => {
  it("maps inactive account to validation hint", () => {
    expect(parseLoginError({ detail: "No active account found with the given credentials" }, 401)).toBe(
      LOGIN_VALIDATION_HINT
    );
  });

  it("maps 401 to validation hint", () => {
    expect(parseLoginError({}, 401)).toBe(LOGIN_VALIDATION_HINT);
  });
});
