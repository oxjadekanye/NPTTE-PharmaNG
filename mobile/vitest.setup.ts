import { vi } from "vitest";

vi.mock("expo-constants", () => ({
  default: {
    expoConfig: { extra: { appEnv: "development", apiBaseUrl: "http://localhost:8000/api/v1" } },
  },
}));
