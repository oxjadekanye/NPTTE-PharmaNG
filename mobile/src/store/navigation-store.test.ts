import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("expo-router", () => ({
  router: { replace: vi.fn() },
}));

import { useNavigationStore } from "@/store/navigation-store";

describe("navigation-store", () => {
  beforeEach(() => {
    useNavigationStore.setState({
      rootMounted: false,
      pendingRoute: null,
      lastRoute: null,
    });
  });

  it("queues replace until root is mounted", () => {
    useNavigationStore.getState().replaceWhenReady("/regulator");
    expect(useNavigationStore.getState().pendingRoute).toBe("/regulator");
    useNavigationStore.getState().setRootMounted();
    expect(useNavigationStore.getState().pendingRoute).toBeNull();
  });

  it("skips duplicate replace to same href", () => {
    useNavigationStore.setState({ rootMounted: true, lastRoute: "/regulator" });
    useNavigationStore.getState().replaceWhenReady("/regulator");
    expect(useNavigationStore.getState().pendingRoute).toBeNull();
  });
});
