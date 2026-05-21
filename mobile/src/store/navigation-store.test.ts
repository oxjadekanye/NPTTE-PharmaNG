import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("expo-router", () => ({
  router: { replace: vi.fn(), push: vi.fn() },
}));

import { useNavigationStore } from "@/store/navigation-store";

describe("navigation-store", () => {
  beforeEach(() => {
    useNavigationStore.setState({
      rootMounted: false,
      currentPath: "/",
      pendingRoute: null,
    });
  });

  it("queues replace until root is mounted", () => {
    useNavigationStore.getState().replaceWhenReady("/regulator");
    expect(useNavigationStore.getState().pendingRoute).toBe("/regulator");
    useNavigationStore.getState().setRootMounted();
    expect(useNavigationStore.getState().pendingRoute).toBeNull();
  });

  it("skips replace when already on target path", () => {
    useNavigationStore.setState({ rootMounted: true, currentPath: "/regulator" });
    useNavigationStore.getState().replaceWhenReady("/regulator");
    expect(useNavigationStore.getState().pendingRoute).toBeNull();
  });

  it("allows replace after clearNavigationDedupe from login path", () => {
    useNavigationStore.setState({ rootMounted: true, currentPath: "/login" });
    useNavigationStore.getState().replaceWhenReady("/pharmacy");
    expect(useNavigationStore.getState().pendingRoute).toBeNull();
  });

  it("queues staff login push until root is mounted", () => {
    useNavigationStore.getState().pushStaffLoginWhenReady("/login");
    expect(useNavigationStore.getState().pendingRoute).toBeNull();
    useNavigationStore.getState().setRootMounted();
  });

  it("clears pending replace before staff login push", () => {
    useNavigationStore.setState({ rootMounted: true, currentPath: "/", pendingRoute: "/regulator" });
    useNavigationStore.getState().pushStaffLoginWhenReady("/login");
    expect(useNavigationStore.getState().pendingRoute).toBeNull();
  });
});
