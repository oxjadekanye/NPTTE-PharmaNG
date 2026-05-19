import { describe, it, expect, vi } from "vitest";
import { enqueueHydration, cancelHydration, HydrationPriority } from "./hydration-queue";

describe("hydration-queue", () => {
  it("runs enqueued tasks", async () => {
    const fn = vi.fn().mockResolvedValue(undefined);
    enqueueHydration("test:one", fn, HydrationPriority.SHELL);
    await new Promise((r) => setTimeout(r, 50));
    expect(fn).toHaveBeenCalled();
  });

  it("cancels pending queued task while slots are busy", async () => {
    const releases: Array<() => void> = [];
    const hold = () =>
      new Promise<void>((resolve) => {
        releases.push(resolve);
      });
    for (let i = 0; i < 3; i++) {
      enqueueHydration(`block:${i}`, () => hold(), HydrationPriority.SHELL);
    }
    const fn = vi.fn().mockResolvedValue(undefined);
    enqueueHydration("test:cancel", fn, HydrationPriority.BACKGROUND);
    cancelHydration("test:cancel");
    releases.forEach((r) => r());
    await new Promise((r) => setTimeout(r, 80));
    expect(fn).not.toHaveBeenCalled();
  });
});
